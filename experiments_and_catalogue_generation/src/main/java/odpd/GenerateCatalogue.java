package odpd;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.apache.jena.ext.com.google.common.collect.Lists;
import org.apache.jena.ext.com.google.common.io.Files;
import org.apache.jena.query.QueryExecutionFactory;
import org.apache.jena.query.ResultSet;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.RDFNode;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.rdf.model.StmtIterator;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.vocabulary.OWL;
import org.apache.jena.vocabulary.OWL2;
import org.apache.jena.vocabulary.RDF;

import freemarker.core.ParseException;
import freemarker.template.MalformedTemplateNameException;
import freemarker.template.Template;
import freemarker.template.TemplateException;
import freemarker.template.TemplateNotFoundException;
import guru.nidi.graphviz.engine.Format;
import guru.nidi.graphviz.engine.Graphviz;
import guru.nidi.graphviz.model.MutableGraph;
import guru.nidi.graphviz.parse.Parser;

public class GenerateCatalogue {

//	public static String removeSuffix(String s) {
//		int last = s.length() - 1;
//		while (last > 0) {
//			if (!Character.isDigit(s.charAt(last))) {
//				break;
//			}
//			last--;
//		}
//		return s.substring(0, last + 1);
//	}

	public static String getSuffix(String s) {
		int last = s.length() - 1;
		while (last > 0) {
			if (!Character.isDigit(s.charAt(last))) {
				break;
			}
			last--;
		}
		if (s.charAt(last) == '-') {
			return s.substring(last + 2, s.length());
		}
		return s.substring(last + 1, s.length());
	}

	private static void extractFragment(String rdfCommunity, String ontologyIn, String fileOut)
			throws FileNotFoundException {
//		System.out.println(ontologyIn);
		Model ontology = ModelFactory.createDefaultModel();
		RDFDataMgr.read(ontology, ontologyIn);

		Model rdfCommunityIn = ModelFactory.createDefaultModel();
		RDFDataMgr.read(rdfCommunityIn, rdfCommunity);

		Model out = ModelFactory.createDefaultModel();

		StmtIterator si = rdfCommunityIn.listStatements();

		Set<String> properties = new HashSet<>();
		si.forEachRemaining(s -> {
			properties.add(s.getPredicate().getURI());
			out.add(getResourceRecursively(s.getPredicate(), ontology));
		});

		si = rdfCommunityIn.listStatements();
		si.forEachRemaining(s -> {
			out.add(getClass(s.getSubject(), properties, ontology));
			out.add(getClass(s.getObject().asResource(), properties, ontology));
		});

		out.write(new FileOutputStream(new File(fileOut)), "TTL");

	}

	private static Model getClass(Resource r, Set<String> properties, Model m) {
		Model result = ModelFactory.createDefaultModel();

		m.listStatements(r, null, (RDFNode) null).forEachRemaining(s -> {
			if (s.getObject().isAnon()) {
				if (m.contains(r, RDF.type, OWL2.Restriction)) {
					RDFNode op = m.listObjectsOfProperty(r, OWL.onProperty).next();
					if (op.isURIResource() && properties.contains(op.asResource().getURI())) {
						result.add(s);
						result.add(getResourceRecursively(r, m));
					}
				}
			} else {
				result.add(s);
			}
		});

		return result;
	}

	private static Model getResourceRecursively(Resource r, Model m) {
		Model result = ModelFactory.createDefaultModel();

		m.listStatements(r, null, (RDFNode) null).forEachRemaining(s -> {
			result.add(s);
			if (s.getObject().isAnon()) {
				getResourceRecursively(s.getObject().asResource(), m);
			}
		});

		return result;
	}

	private static List<Cluster> getClusters(String clusterFilepath, String folderIn, String folderOut,
			String ontologyFolder, Map<Integer, Set<Integer>> clusterHierarhcy,
			Map<List<Integer>, Double> subsumptionStrength) throws IOException {
		Reader in = new FileReader(clusterFilepath);
		CSVParser records = CSVFormat.DEFAULT.parse(in);
		Iterator<CSVRecord> it = records.iterator();
		it.next(); // discard headers
		List<Cluster> result = new ArrayList<>();
		Map<Integer, Cluster> id2Cluster = new HashMap<>();

		while (it.hasNext()) {
			CSVRecord r = (CSVRecord) it.next();
			Integer clusterId = Integer.parseInt(r.get(1));
			String id = "cluster" + r.get(1);
			String name = cleanName(r.get(2));
			String description = r.get(2);
			String img = "";
			List<WeightedSpecialization> superClusters = Lists.newArrayList();
			List<Community> communities = new ArrayList<>();

			String[] communitiesStrings = r.get(11).split("\n");
			String[] communitiyDocs = r.get(12).split("\n");
			for (int i = 0; i < communitiesStrings.length; i++) {
				String communityString = communitiesStrings[i];
//				System.out.println("Community "+communityString);
				String communityId = communityString;
				String communityName = communityString;

				String dotFile = folderIn + "/communities_images/" + AnalyseAlignments.removeSuffix(communityId)
						+ "/Community" + getSuffix(communityId);

				if (!new File(dotFile).exists()) {
					System.err.println(dotFile);
					System.err.println(communityId);
					System.err.println(getSuffix(communityId));
				}

				String communityImg = folderOut + "/img/" + communityId + ".png";
				dotTOPNG(dotFile, communityImg);

				String ontologyFileIn = ontologyFolder + "/" + AnalyseAlignments.removeSuffix(communityId) + ".owl";
				if (!new File(ontologyFileIn).exists()) {
					ontologyFileIn = ontologyFolder + "/" + AnalyseAlignments.removeSuffix(communityId) + ".ttl";
					if (!new File(ontologyFileIn).exists()) {
						System.err.println("Not found " + ontologyFileIn);
					}
				}

				String communityRDF = folderIn + "/communities_original_rdf/"
						+ AnalyseAlignments.removeSuffix(communityId) + "/" + communityId + "_intensional.ttl";
				String communityRDFOut = folderOut + "/ontologies/" + communityId + ".ttl";

				extractFragment(communityRDF, ontologyFileIn, communityRDFOut);

				String ontologyName = extractOntologyName(ontologyFileIn);

				FileUtils.copyFile(new File(ontologyFileIn),
						new File(folderOut + "/ontologies/" + FilenameUtils.getName(ontologyFileIn)));

				String doc = communitiyDocs[i];
				String ontology = "ontologies/" + FilenameUtils.getName(ontologyFileIn);
				String communityOWL = "ontologies/" + communityId + ".ttl";

//				String communityImg = communityString;
				Community c = new Community(communityId, communityName, communityImg.replace(folderOut+"/", ""),
						communityOWL, ontology, doc, ontologyName);
				communities.add(c);
			}

			Cluster newCluster = new Cluster(id, name, description, img, superClusters, communities);
			result.add(newCluster);
			id2Cluster.put(clusterId, newCluster);
		}

		id2Cluster.keySet().forEach(clusterId -> {
			List<WeightedSpecialization> superClusters = new ArrayList<>();
			if (clusterHierarhcy.containsKey(clusterId)) {
				clusterHierarhcy.get(clusterId).forEach(superC -> {
					Cluster superCluster = id2Cluster.get(superC);
					if (superCluster != null) {
						double strenght = subsumptionStrength.get(Lists.newArrayList(clusterId, superC));
						superClusters.add(new WeightedSpecialization(strenght, superCluster));
					} else {
//						System.err.println("Couldn't find cluster " + superC);
					}
				});

				Collections.sort(superClusters, new Comparator<WeightedSpecialization>() {
					@Override
					public int compare(WeightedSpecialization o1, WeightedSpecialization o2) {
						return -1 * Double.compare(o1.getStrength(), o2.getStrength());
					}
				});

				id2Cluster.get(clusterId).setSuperClusters(superClusters);
			} else {
				System.err.println(".Couldn't find cluster " + clusterId);
			}
		});

		id2Cluster.keySet().forEach(k -> {

//			Collections.sort(id2Cluster.get(k), new Comparator<WeightedSpecialization>() {
//				
//			});
		});

		return result;
	}

	private static String cleanName(String communityString) {
		if (communityString.startsWith("synset")) {
			return Character.toUpperCase(communityString.split("-")[1].charAt(0))
					+ communityString.split("-")[1].substring(1);
		}
		return communityString.replace("_", " ");
	}

	private static String extractOntologyName(String ontologyFileIn) {
		Model m = ModelFactory.createDefaultModel();
		RDFDataMgr.read(m, ontologyFileIn);

		String query = "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX dc: <http://purl.org/dc/elements/1.1/> SELECT DISTINCT ?ontologyName {?o a owl:Ontology .?o dc:title ?ontologyName  } LIMIT 1";

		ResultSet rs = QueryExecutionFactory.create(query, m).execSelect();

		if (rs.hasNext()) {
			return rs.next().get("ontologyName").asLiteral().getValue().toString();
		}

		return FilenameUtils.getBaseName(ontologyFileIn);
	}

	public static void addDescriptions(List<Cluster> clusters) {
		for (Cluster c : clusters) {
			Set<String> terminology = new HashSet<>();
			c.getCommunities().forEach(commuity -> {
				for (String term : commuity.getDescription().split(" ")) {
					terminology.add(term);
				}
			});
			c.setDescription(String.join(" ", terminology));
		}
	}

	public static void generateCatalogue(String folderOut, String clustersFile, String folderIn,
			String folderOntologiesIn, String topLevelAnchestorsFile, String hierarchyFile,
			String generatedCommunitiesFolder, String corpusName, String numberOfOntologies)
			throws TemplateNotFoundException, MalformedTemplateNameException, ParseException, IOException,
			TemplateException {

		new File(folderOut).mkdir();
		new File(folderOut + "/img").mkdir();
		new File(folderOut + "/ontologies").mkdir();

		Map<String, Set<String>> topLevelAnchestors = AnalyseAlignments.loadHierarhcy(topLevelAnchestorsFile);
		Map<List<Integer>, Double> subsumptionStrength = new HashMap<>();
		Map<String, Set<String>> hierarchy = AnalyseAlignments.loadHierarhcy(hierarchyFile);
		Map<Integer, Set<Integer>> clusterHierarhcy = new HashMap<>();
		double[][] sim = AnalyseAlignments.clusterSimilarity(clustersFile, topLevelAnchestors, hierarchy,
				clusterHierarhcy, subsumptionStrength, 0.0);

		Template temp = TransformerConfiguration.getInstance().getFreemarkerCfg().getTemplate("templates/index.html");
		Template clusterTemp = TransformerConfiguration.getInstance().getFreemarkerCfg()
				.getTemplate("templates/cluster.html");

		List<Cluster> clusters = getClusters(clustersFile, generatedCommunitiesFolder, folderOut, folderOntologiesIn,
				clusterHierarhcy, subsumptionStrength);
		addDescriptions(clusters);
		Collections.shuffle(clusters);

		Map<String, Object> index = new HashMap<String, Object>();
		index.put("clusters", clusters);
		index.put("numberOfOntologies", numberOfOntologies);
		index.put("corpusName", corpusName);

		for (Cluster c : clusters) {
			Map<String, Object> cluster = new HashMap<String, Object>();
			cluster.put("cluster", c);
			PrintWriter pwc = new PrintWriter(new File(folderOut + "/" + c.getId() + ".html"));
			clusterTemp.process(cluster, pwc);
			pwc.flush();
			pwc.close();
		}

		PrintWriter pw = new PrintWriter(new File(folderOut + "/index.html"));

		Files.copy(new File("src/main/resources/templates/jumbotron.css"), new File(folderOut + "/jumbotron.css"));
		FileUtils.copyDirectory(new File("src/main/resources/templates/assets"), new File(folderOut + "/assets"));

		temp.process(index, pw);

		pw.flush();
		pw.close();
	}

	public static void dotTOPNG(String dotFile, String png) throws IOException {
		InputStream dot = new FileInputStream(new File(dotFile));
		MutableGraph g = new Parser().read(dot);
		Graphviz.fromGraph(g).width(700).render(Format.PNG).toFile(new File(png));
	}

	public static void main(String[] args) {
		try {
			String folderIn = args[0];
			String folderOut = args[1];
			String corpusName = args[2];
			String numberOntologies = args[3];
			String clusterFile = args[4];
			String generatedCommunitiesFolder = args[5];
			String ontologiesInput = args[6];
			generateCatalogue(folderOut, folderIn + clusterFile, folderIn, folderIn + ontologiesInput,
					folderIn + "/topLevelAnchestors.csv", folderIn + "/framehierarchy.csv",
					folderIn + generatedCommunitiesFolder, corpusName, numberOntologies);

		} catch (IOException | TemplateException e) {
			e.printStackTrace();
		}
	}
}
