package odpd;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.Reader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;
import org.apache.commons.io.FilenameUtils;
import org.apache.jena.ext.com.google.common.collect.Lists;
import org.apache.jena.ext.com.google.common.collect.Sets;
import org.apache.jena.query.QueryExecution;
import org.apache.jena.query.QueryExecutionFactory;
import org.apache.jena.query.QuerySolution;
import org.apache.jena.query.ResultSet;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Statement;
import org.apache.jena.rdf.model.StmtIterator;
import org.apache.jena.riot.RDFDataMgr;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.formats.TurtleDocumentFormat;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.OWLOntologyStorageException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.util.concurrent.AtomicDouble;

import guru.nidi.graphviz.engine.Format;
import guru.nidi.graphviz.engine.Graphviz;
import guru.nidi.graphviz.model.MutableGraph;
import guru.nidi.graphviz.parse.Parser;

public class AnalyseAlignments {

	private static Logger logger = LoggerFactory.getLogger(AnalyseAlignments.class);

	public static void unifyAlignments(String folderPath, String fileOut)
			throws OWLOntologyCreationException, OWLOntologyStorageException {
		logger.trace("Creating OWL ontology manager");
		OWLOntologyManager manager = OWLManager.createOWLOntologyManager();

		OWLOntology ontology = manager.createOntology();

		File folder = new File(folderPath);

		for (File child : folder.listFiles()) {
			logger.info("Processing {}", child.getAbsolutePath());
			if (FilenameUtils.isExtension(child.getName(), "rdf")) {
				OWLOntology align = manager.loadOntologyFromOntologyDocument(child);
				ontology.addAxioms(align.axioms());
			}
		}

		logger.info("Number of triples within alignments {}", ontology.axioms().count());

		ontology.saveOntology(new TurtleDocumentFormat(), IRI.create("file:" + fileOut));

	}

	public static String removeSuffix(String s) {
		int last = s.length() - 1;
		while (last > 0) {
			if (!Character.isDigit(s.charAt(last))) {
				break;
			}
			last--;
		}

		if (s.charAt(last) == '-') {
			return s.substring(0, last + 2);
		}

		return s.substring(0, last + 1);
	}

	public static void analyseAlignments(String clusterFilepath, String folder, String amlAlignments,
										 String assertedAlingmentsFile, String outfolder, String topLevelAnchestorsFile, String hierarchyFile,
										 double thresholdSubsumptions, boolean conf) throws IOException {

		Map<String, Set<String>> topLevelAnchestors = loadHierarhcy(topLevelAnchestorsFile);
		Map<List<Integer>, Double> subsumptionStrength = new HashMap<>();
		Map<String, Set<String>> hierarchy = loadHierarhcy(hierarchyFile);
		Map<Integer, Set<Integer>> clusterHierarhcy = new HashMap<>();
		double[][] sim = clusterSimilarity(clusterFilepath, topLevelAnchestors, hierarchy, clusterHierarhcy,
				subsumptionStrength, thresholdSubsumptions);

		Map<String, Set<Integer>> uri2Cluster = new HashMap<>();
		computeUri2ClusterMap(clusterFilepath, folder, uri2Cluster);

		Map<Set<String>, Double> scores = new HashMap<>();
		Set<Set<String>> alignmentSetAll = new HashSet<Set<String>>();
		Set<Set<String>> alignmentSet099 = new HashSet<Set<String>>();
		Set<Set<String>> alignmentSet090 = new HashSet<Set<String>>();
		Set<Set<String>> assertedAlignmentsEquivalences = new HashSet<Set<String>>();
		Set<Set<String>> assertedAlignmentsSubsumptions = new HashSet<Set<String>>();

		Set<Set<String>> assertedAlignmentsAlignments = new HashSet<Set<String>>();

		retrieveAlignments(amlAlignments, alignmentSetAll, scores, 0.0);
		retrieveAlignments(amlAlignments, alignmentSet090, scores, 0.90);
		retrieveAlignments(amlAlignments, alignmentSet099, scores, 0.99);
		retrieveEquivalences(assertedAlingmentsFile, assertedAlignmentsEquivalences);
		retrieveSubsumptions(assertedAlingmentsFile, assertedAlignmentsSubsumptions);

//		System.out.println("Retrieved equivalences: " + assertedAlignmentsEquivalences.size());

		assertedAlignmentsAlignments.addAll(assertedAlignmentsEquivalences);
		assertedAlignmentsAlignments.addAll(assertedAlignmentsSubsumptions);

		System.out.println("Assessing AML Alignments on Asserted Alignements: "
				+ ((double) Sets.intersection(alignmentSetAll, assertedAlignmentsAlignments).size()
				/ (double) assertedAlignmentsAlignments.size()));

//		computePrecisionOfWithRespectToAlignments(assertedAlignmentsEquivalences, null, uri2Cluster,
//				outfolder + "/Asserted_alingments", "Asserted_alingments", sim, clusterHierarhcy);
//		computePrecisionOfWithRespectToAlignments(assertedAlignmentsSubsumptions, null, uri2Cluster,
//				outfolder + "/Asserted_subsumptions", "Asserted_subsumptions", sim, clusterHierarhcy);

		if (!conf) {
			computePrecisionOfWithRespectToAlignments(assertedAlignmentsAlignments, null, uri2Cluster,
					outfolder + "/Asserted_alignments", "Asserted_alignments", sim, clusterHierarhcy);
			System.out.println();
			computePrecisionOfWithRespectToAlignments(alignmentSetAll, scores, uri2Cluster, outfolder + "/AML_All",
					"AML_All", sim, clusterHierarhcy);
			System.out.println();
			computePrecisionOfWithRespectToAlignments(alignmentSet090, scores, uri2Cluster, outfolder + "/AML_090",
					"AML_090", sim, clusterHierarhcy);
			System.out.println();
			computePrecisionOfWithRespectToAlignments(alignmentSet099, scores, uri2Cluster, outfolder + "/AML_099",
					"AML_099", sim, clusterHierarhcy);
		} else {
//			computePrecisionOfWithRespectToAlignments(assertedAlignmentsAlignments, null, uri2Cluster,
//					outfolder + "/Asserted_alignments", "Asserted_alignments", sim, clusterHierarhcy);
//			System.out.println();
			computePrecisionOfWithRespectToAlignments(alignmentSetAll, scores, uri2Cluster, outfolder + "/CA",
					"CA", sim, clusterHierarhcy);
		}

//		System.out.println(clusterHierarhcy);

		int sum = 0;
		int max = 0;
		for (Integer cluster : clusterHierarhcy.keySet()) {
			sum += clusterHierarhcy.get(cluster).size();
			max = Math.max(clusterHierarhcy.get(cluster).size(), max);
		}

		double avg = (double) sum / clusterHierarhcy.size();
//
		double sumSimilarity = 0.0;
		int[] simPerRange = new int[10];

		FileOutputStream fos = new FileOutputStream(new File(outfolder + "/similarities"));

		for (int i = 0; i < sim.length; i++) {
			for (int j = 0; j < sim[i].length; j++) {
				sumSimilarity += sim[i][j];
				fos.write((sim[i][j] + "\n").getBytes());

				for (int k = 0; k < simPerRange.length; k++) {
					if (sim[i][j] >= (k) * 0.1 && sim[i][j] < (k + 1) * 0.1) {
						simPerRange[k]++;
					}
				}

			}
		}

		fos.flush();
		fos.close();

		System.out.println("Average number of super clusters: " + avg + "\nMaximum number of super clusters: " + max
				+ "\nTotal Number of Cluster relations: " + sum);
		System.out.println("Avg Cluster Similarity: " + (sumSimilarity / (sim.length * sim.length)));
//		for (int i = 0; i < simPerRange.length; i++) {
//			System.out.println("[" + i * 0.1 + ", " + (i + 1) * 0.1 + ") " + simPerRange[i]);
//		}

//		System.out.println("=" + 1.0 + " " + 100);
//		System.out.println("Distribution similarity: " + Arrays.toString(simPerRange) + " ");

//		System.out.println(subsumptionStrength);

//		System.out.println(subsumptionStrength);

	}

	private static void reviseStrength(Map<List<Integer>, Double> subsumptionStrength) {

		double max = 0.0;
		for (List<Integer> k : subsumptionStrength.keySet()) {
			max = Math.max(max, subsumptionStrength.get(k));
		}

		for (List<Integer> k : subsumptionStrength.keySet()) {
			subsumptionStrength.put(k, subsumptionStrength.get(k) / max);
		}

	}

	private static void reviseStrengthMax(Map<List<Integer>, Double> subsumptionStrength, double max) {

//		double max = 0.0;
//		for (List<Integer> k : subsumptionStrength.keySet()) {
//			max = Math.max(max, subsumptionStrength.get(k));
//		}

		for (List<Integer> k : subsumptionStrength.keySet()) {
			subsumptionStrength.put(k, subsumptionStrength.get(k) / max);
		}

	}

	public static void computeUri2ClusterMap(String clusterFilepath, String folder,
											 Map<String, Set<Integer>> uri2Cluster) throws IOException {
		Reader in = new FileReader(clusterFilepath);
		CSVParser records = CSVFormat.DEFAULT.parse(in);
		Iterator<CSVRecord> it = records.iterator();
		it.next(); // discard headers
		Model m;

		while (it.hasNext()) {
			CSVRecord csvRecord = (CSVRecord) it.next();

			Integer cluster = Integer.parseInt(csvRecord.get(1));
			String[] communities = csvRecord.get(11).split("\n");

			for (String community : communities) {
				String rdfCommunity = folder + "/" + removeSuffix(community) + "/" + community + "_intensional.ttl";
				m = ModelFactory.createDefaultModel();
				m.read(rdfCommunity);
				StmtIterator si = m.listStatements();
				while (si.hasNext()) {
					Statement s = si.next();
					String subj = s.getSubject().getURI();
					String pred = s.getPredicate().getURI();
					String obj = s.getObject().asResource().getURI();

					addToCluster(uri2Cluster, subj, cluster);
					addToCluster(uri2Cluster, pred, cluster);
					addToCluster(uri2Cluster, obj, cluster);

				}
			}
		}
	}

	public static Map<String, Set<String>> loadHierarhcy(String topLevelAnchestestorsFile) throws IOException {
		Reader in = new FileReader(topLevelAnchestestorsFile);
		CSVParser records = CSVFormat.DEFAULT.withQuote('"').parse(in);
		Iterator<CSVRecord> it = records.iterator();
		it.next(); // discard headers

		Map<String, Set<String>> result = new HashMap<>();

		while (it.hasNext()) {
			CSVRecord csvRecord = (CSVRecord) it.next();

			Set<String> anchestors = new HashSet<>();
			for (String f : csvRecord.get(1).trim().split(" ")) {

				anchestors.add(f.replace("\"", "").replace("https://w3id.org/framester/framenet/abox/frame/", "frame:")
						.trim());
			}

			result.put(csvRecord.get(0).replace("\"", "")
					.replace("https://w3id.org/framester/framenet/abox/frame/", "frame:").trim(), anchestors);

		}

//		System.out.println(result.keySet());
//		System.out.println(result.keySet().iterator().next());
//		System.out.println(result.get("frame:Apply_heat"));
//		System.out.println(result.get("frame:Visitor_and_host"));

		return result;
	}

	public static double[][] clusterSimilarity(String clusterFilepath, Map<String, Set<String>> topLevelAnchestors,
											   Map<String, Set<String>> hierarchy, Map<Integer, Set<Integer>> clusterHierarhcy,
											   Map<List<Integer>, Double> subsumptionStrength, double threshold) throws IOException {

		Map<Integer, Set<Integer>> clusterHierarhcyCandidate = new HashMap<>();
		Map<List<Integer>, Double> subsumptionStrengthCandidate = new HashMap<>();

		Reader in = new FileReader(clusterFilepath);
		CSVParser records = CSVFormat.DEFAULT.parse(in);
		Iterator<CSVRecord> it = records.iterator();
		it.next(); // discard headers

//		Map<Integer, Set<String>> clusterToEntities = new HashMap<>();
		Map<Integer, Map<String, Integer>> clusterToEntities = new HashMap<>();

		while (it.hasNext()) {
			CSVRecord csvRecord = (CSVRecord) it.next();

			Integer cluster = Integer.parseInt(csvRecord.get(1));

			String[] frames2frequency = csvRecord.get(6).split("\n");
			String[] syn2frequency = csvRecord.get(7).split("\n");

			Map<String, Integer> entities = new HashMap<>();
			for (String f2f : frames2frequency) {
				if(f2f.equals("no frames"))
					continue;
				String frame = "frame:" + f2f.split(":")[1];
				Integer freq = Integer.parseInt(f2f.split(":")[2].trim());
				entities.put(frame, freq);
				Set<String> tla = topLevelAnchestors.get("frame:" + frame);
				if (tla != null) {
					tla.forEach(t -> {
//						entities.put(t, freq);
					});
				} else {
//					System.err.println("couldn't find tla for frame:" + frame);
				}
			}

			for (String s2f : syn2frequency) {
				String syn = s2f.split(":")[1];
				Integer freq = Integer.parseInt(s2f.split(":")[2].trim());
				entities.put(syn, freq);
			}

			clusterToEntities.put(cluster, entities);

		}
		System.out.println("Number of clusters " + clusterToEntities.size());
		double[][] result = new double[clusterToEntities.size()][clusterToEntities.size()];

		for (Integer c1 : clusterToEntities.keySet()) {
			for (Integer c2 : clusterToEntities.keySet()) {
				result[c1][c2] = (double) (Sets.intersection(clusterToEntities.get(c1).keySet(),
						clusterToEntities.get(c2).keySet())).size()
						/ Math.min(clusterToEntities.get(c1).size(), clusterToEntities.get(c2).size());
			}
		}

		double max_freq = 0.0;

		for (Integer c1 : clusterToEntities.keySet()) {
			for (Integer c2 : clusterToEntities.keySet()) {
				if (c1 < c2) {

					double c1c2 = 0;
					double c2c1 = 0;
					if (subsumptionStrengthCandidate.containsKey(Lists.newArrayList(c1, c2))) {
						c1c2 = subsumptionStrengthCandidate.get(Lists.newArrayList(c1, c2));
					}

					if (subsumptionStrengthCandidate.containsKey(Lists.newArrayList(c2, c1))) {
						c2c1 = subsumptionStrengthCandidate.get(Lists.newArrayList(c2, c1));
					}

					Set<String> fCluster1 = clusterToEntities.get(c1).keySet();
					Set<String> fCluster2 = clusterToEntities.get(c2).keySet();
					double c1_total_freq = 0.0;
					double c2_total_freq = 0.0;

					for (String f1 : fCluster1) {
						c1_total_freq += clusterToEntities.get(c1).get(f1);
						for (String f2 : fCluster2) {
							c2_total_freq += clusterToEntities.get(c2).get(f2);
							if (hierarchy.get(f1) != null && hierarchy.get(f1).contains(f2)) {
								Set<Integer> superC1 = clusterHierarhcyCandidate.get(c1);
								if (superC1 == null) {
									superC1 = new HashSet<>();
								}
								superC1.add(c2);
//								c1c2++;
								c1c2 += clusterToEntities.get(c1).get(f1);
								clusterHierarhcyCandidate.put(c1, superC1);
							}

							if (hierarchy.get(f2) != null && hierarchy.get(f2).contains(f1)) {
								Set<Integer> superC2 = clusterHierarhcyCandidate.get(c2);
								if (superC2 == null) {
									superC2 = new HashSet<>();
								}
								superC2.add(c1);
//								c2c1++;
								c2c1 += clusterToEntities.get(c2).get(f2);
								clusterHierarhcyCandidate.put(c2, superC2);
							}
						}
					}
					if (c1c2 > 0) {
						subsumptionStrengthCandidate.put(Lists.newArrayList(c1, c2), c1c2);
					}

					if (c2c1 > 0) {
						subsumptionStrengthCandidate.put(Lists.newArrayList(c2, c1), c2c1);
					}

					max_freq = Math.max(Math.max(c1c2, c2c1), max_freq);
				}

			}
		}

		reviseStrengthMax(subsumptionStrengthCandidate, max_freq);

		printDistribution(subsumptionStrengthCandidate);

		filter(clusterHierarhcyCandidate, subsumptionStrengthCandidate, threshold);

		printDistribution(subsumptionStrengthCandidate);

		subsumptionStrength.putAll(subsumptionStrengthCandidate);
		clusterHierarhcy.putAll(clusterHierarhcyCandidate);

		return result;
	}

	private static void printDistribution(Map<List<Integer>, Double> subsumptionStrengthCandidate) {
		int[] simPerRange = new int[10];
		int equalToOne = 0;

		Iterator<List<Integer>> pairsIt = subsumptionStrengthCandidate.keySet().iterator();

		while (pairsIt.hasNext()) {
			List<java.lang.Integer> list = (List<java.lang.Integer>) pairsIt.next();
			double s = subsumptionStrengthCandidate.get(list);
			for (int k = 0; k < simPerRange.length; k++) {
				if (s >= (k) * 0.1 && s < (k + 1) * 0.1) {
					simPerRange[k]++;
				}
				if (s == 1.0) {
					equalToOne++;
				}
			}
		}

//		System.out.println("strength similarity distribution");
//		System.out.println(Arrays.toString(simPerRange));
//		System.out.println("equal to 1 " + equalToOne);

	}

	private static void filter(Map<Integer, Set<Integer>> clusterHierarhcyCandidate,
							   Map<List<Integer>, Double> subsumptionStrengthCandidate, final double threshold) {

		List<List<Integer>> toRemove = new ArrayList<>();
		subsumptionStrengthCandidate.forEach((k, v) -> {
			if (v < threshold) {
				clusterHierarhcyCandidate.get(k.get(0)).remove(k.get(1));
				toRemove.add(k);
			}
		});

		toRemove.forEach(tr -> {
			subsumptionStrengthCandidate.remove(tr);
		});
	}

	public static double mapSimilarity(Map<String, Integer> m1, Map<String, Integer> m2) {
		double n1 = norm(m1);
		double n2 = norm(m2);
		double sum = 0.0;
		for (String k : Sets.intersection(m1.keySet(), m2.keySet())) {
			sum += m1.get(k) * m2.get(k);
		}
		return sum / (n1 * n2);
	}

	public static double norm(Map<String, Integer> m1) {
		int sum = 0;
		for (String k : m1.keySet()) {
			sum += m1.get(k) * m1.get(k);
		}
		return Math.sqrt(sum);
	}

	public static void computePrecisionOfWithRespectToAlignments(Set<Set<String>> alignmentSet,
																 Map<Set<String>, Double> scores, Map<String, Set<Integer>> uri2Cluster, String outfolder,
																 String datasetName, final double[][] sim, Map<Integer, Set<Integer>> clusterHierarhcy) throws IOException {

		new File(outfolder).mkdir();

		AtomicInteger innerAlignments = new AtomicInteger();
		AtomicDouble innerAlignmentsConfidence = new AtomicDouble();
		AtomicInteger validAlignments = new AtomicInteger();
		AtomicDouble validAlignmentsConfidence = new AtomicDouble();
		AtomicInteger havingHierarchicalRelation = new AtomicInteger();
		AtomicDouble havingHierarchicalConfidence = new AtomicDouble();
		AtomicDouble similaritySum = new AtomicDouble();

		CSVPrinter csvp = new CSVPrinter(
				new FileWriter(new File(outfolder + "/alignments_to_clusters_" + datasetName + ".csv")),
				CSVFormat.DEFAULT);
		CSVPrinter csvpnsc = new CSVPrinter(
				new FileWriter(
						new File(outfolder + "/alignments_to_clusters_not_same_cluster_" + datasetName + ".csv")),
				CSVFormat.DEFAULT);
		FileOutputStream fos = new FileOutputStream(
				new File(outfolder + "/entities_outside_clusters_" + datasetName + ".txt"));

		Set<String> alignedEntitiesNotInCluster = new HashSet<>();

		alignmentSet.forEach(a -> {
			if (a.size() == 2) {
				Iterator<String> els = a.iterator();
				String e1 = els.next();
				String e2 = els.next();

//				String score = "1.0";
//				if (scores != null) {
//					score = scores.get(a);
//				}else {
//					System.out.println("Score null");
//				}

				double s = 1.0;
				if (scores != null) {
					s = scores.get(a);
				}

				Set<Integer> clustersE1 = uri2Cluster.get(e1);
				Set<Integer> clustersE2 = uri2Cluster.get(e2);

				if (clustersE1 != null && clustersE2 != null) {

					double maxSim = 0.0;
					Set<String> clusterHierarchyRel = new HashSet<>();
					for (Integer c1 : clustersE1) {
						for (Integer c2 : clustersE2) {
							maxSim = Math.max(maxSim, sim[c1][c2]);
							if (clusterHierarhcy.get(c1) != null && clusterHierarhcy.get(c1).contains(c2)) {
								// c1 subclusterof c2
								clusterHierarchyRel.add(c1 + " subClusterOf " + c2);
							}

							if (clusterHierarhcy.get(c2) != null && clusterHierarhcy.get(c2).contains(c1)) {
								// c1 subclusterof c2
								clusterHierarchyRel.add(c2 + " subClusterOf " + c1);
							}
						}
					}

					validAlignmentsConfidence.addAndGet(s);
					validAlignments.incrementAndGet();
					if (Sets.intersection(clustersE1, clustersE2).size() > 0) {
						innerAlignments.incrementAndGet();
						innerAlignmentsConfidence.addAndGet(s);
						try {
							csvp.printRecord(e1, e2, clustersE1, clustersE2, s + "", maxSim,
									String.join(", ", clusterHierarchyRel));
						} catch (IOException e) {
							e.printStackTrace();
						}
					} else {
//						System.err.println("Outer " + a);
						similaritySum.addAndGet(maxSim);
						if (!clusterHierarchyRel.isEmpty()) {
							havingHierarchicalRelation.incrementAndGet();
							havingHierarchicalConfidence.addAndGet(s);
						}

						try {
							csvpnsc.printRecord(e1, e2, clustersE1, clustersE2, s, maxSim,
									String.join(", ", clusterHierarchyRel));
						} catch (IOException e) {
							e.printStackTrace();
						}
					}

				} else {
					Iterator<String> i = a.iterator();
					alignedEntitiesNotInCluster.add(i.next());
					alignedEntitiesNotInCluster.add(i.next());

				}

			}
		});

		csvp.flush();
		csvp.close();

		csvpnsc.flush();
		csvpnsc.close();

		alignedEntitiesNotInCluster.forEach(en -> {
			try {
				fos.write((en + "\n").getBytes());
			} catch (IOException e) {
				e.printStackTrace();
			}
		});

		fos.flush();
		fos.close();

//		FileOutputStream fosStat = new FileOutputStream(new File(outfolder + "/stat.txt"));

		int outerAlingments = validAlignments.get() - innerAlignments.get();
		double similarityOuterAlignments = similaritySum.get() / (double) outerAlingments;

//		fosStat.write(("Size of I: " + innerAlignments.get() + "\n").getBytes());
//		fosStat.write(("Size of H: " + havingHierarchicalRelation.get() + "\n").getBytes());
//		fosStat.write(("Outer Alignments: " + outerAlingments + "\n").getBytes());
//		fosStat.write(("Avg. Similarity Outer Alignments: " + similarityOuterAlignments + "\n").getBytes());
//		fosStat.write(("Valid Alignments: " + validAlignments.get() + "\n").getBytes());
//		fosStat.write(("Ratio + having hierarchical rel: "
//				+ ((double) (innerAlignments.get() + havingHierarchicalRelation.get()) / (double) validAlignments.get())
//				+ "\n").getBytes());
//		fosStat.write(
//				("Ratio : " + ((double) innerAlignments.get() / (double) validAlignments.get()) + "\n").getBytes());

		System.out.println("[" + datasetName + "] Size of I: " + innerAlignments.get());
		System.out.println("[" + datasetName + "] Size of H: " + havingHierarchicalRelation.get());
//		System.out.println("[" + datasetName + "] Outer Alignments edges: " + outerAlingments);
//		System.out.println("[" + datasetName + "] Similarity Outer Alignments edges: " + similarityOuterAlignments);
		System.out.println("[" + datasetName + "] Number of Reference Alignments: " + validAlignments.get());
//		System.out.println(
//				"[" + datasetName + "] Aligned Entities not in a cluster " + alignedEntitiesNotInCluster.size());
//		System.out.println(
//				"[" + datasetName + "] Corr on I: " + ((double) innerAlignments.get() / (double) validAlignments.get()));
//		System.out.println("[" + datasetName + "] Corr on H: "
//				+ ((double) (innerAlignments.get() + havingHierarchicalRelation.get())
//						/ (double) validAlignments.get()));

//		System.out.println("Total confidence " + validAlignmentsConfidence.get());
//		System.out.println("Inner alignment confidence " + innerAlignmentsConfidence.get());

		System.out.println("[" + datasetName + "] Corr with respect to I: "
				+ (innerAlignmentsConfidence.get() / validAlignmentsConfidence.get()));
		System.out.println("[" + datasetName + "] Corr with respect to H: "
				+ ((double) (innerAlignmentsConfidence.get() + havingHierarchicalConfidence.get())
				/ validAlignmentsConfidence.get()));

//		fosStat.flush();
//		fosStat.close();
	}

	public static void retrieveAlignments(String alignmentsFile, Set<Set<String>> alignments,
										  Map<Set<String>, Double> scores, double threshold) {

//		Set<Set<String>> alignments = new HashSet<>();

		System.out.println("Retrieving alignments from " + alignmentsFile);

		Model alignmentsModel = ModelFactory.createDefaultModel();
		RDFDataMgr.read(alignmentsModel, alignmentsFile);

		String retrieveAlignments = " SELECT * {"
				+ " ?al a <http://knowledgeweb.semanticweb.org/heterogeneity/alignmentCell> ."
				+ " ?al <http://knowledgeweb.semanticweb.org/heterogeneity/alignmententity1> ?en1 . "
				+ " ?al <http://knowledgeweb.semanticweb.org/heterogeneity/alignmententity2> ?en2 . "
				+ " ?al <http://knowledgeweb.semanticweb.org/heterogeneity/alignmentmeasure> ?score . "
				+ " ?al <http://knowledgeweb.semanticweb.org/heterogeneity/alignmentrelation> ?relation . "
				+ " FILTER (?score >= " + threshold + ")" + "  } ";

//		String retrieveAlignments = " SELECT DISTINCT ?relation {"
//				+ " ?al a <http://knowledgeweb.semanticweb.org/heterogeneity/alignmentCell> ."
//				+ " ?al <http://knowledgeweb.semanticweb.org/heterogeneity/alignmententity1> ?en1 . "
//				+ " ?al <http://knowledgeweb.semanticweb.org/heterogeneity/alignmententity2> ?en2 . "
//				+ " ?al <http://knowledgeweb.semanticweb.org/heterogeneity/alignmentmeasure> ?score . "
//				+ " ?al <http://knowledgeweb.semanticweb.org/heterogeneity/alignmentrelation> ?relation . "
//				+ " FILTER (?score >= " + threshold + ")" + "  } ";
//
//		System.out.println(ResultSetFormatter
//				.asText(QueryExecutionFactory.create(retrieveAlignments, alignmentsModel).execSelect()));

		QueryExecution qexex = QueryExecutionFactory.create(retrieveAlignments, alignmentsModel);
		ResultSet rs = qexex.execSelect();
		double sum = 0.0;
		double total = 0.0;

		while (rs.hasNext()) {
			QuerySolution qs = (QuerySolution) rs.next();
			Set<String> alignment = Sets.newHashSet(qs.get("en1").asResource().getURI(),
					qs.get("en2").asResource().getURI());
//			System.out.println(qs.get("score").asLiteral().getDouble());
			sum += qs.get("score").asLiteral().getDouble();
			total += 1.0;
			scores.put(alignment, qs.get("score").asLiteral().getDouble());
			alignments.add(alignment);

		}
		System.out.println("Average confidence of the alignments " + sum / total);

	}

	public static void retrieveEquivalences(String alignmentsFile, Set<Set<String>> alignments) {

		Model alignmentsModel = ModelFactory.createDefaultModel();
		RDFDataMgr.read(alignmentsModel, alignmentsFile);

		String retrieveAlignments = "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT * {"
				+ " ?en1 owl:equivalentClass|owl:equivalentProperty ?en2 " + "  } ";

		QueryExecution qexex = QueryExecutionFactory.create(retrieveAlignments, alignmentsModel);
		ResultSet rs = qexex.execSelect();

		while (rs.hasNext()) {
			QuerySolution qs = (QuerySolution) rs.next();
			Set<String> alignment = Sets.newHashSet(qs.get("en1").asResource().getURI(),
					qs.get("en2").asResource().getURI());
			alignments.add(alignment);
		}
	}

	public static void retrieveSubsumptions(String alignmentsFile, Set<Set<String>> alignments) {

		Model alignmentsModel = ModelFactory.createDefaultModel();
		RDFDataMgr.read(alignmentsModel, alignmentsFile);

		String retrieveAlignments = "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT * {"
				+ " ?en1 rdfs:subClassOf|rdfs:subPropertyOf ?en2 " + "  } ";

		QueryExecution qexex = QueryExecutionFactory.create(retrieveAlignments, alignmentsModel);
		ResultSet rs = qexex.execSelect();

		while (rs.hasNext()) {
			QuerySolution qs = (QuerySolution) rs.next();
			Set<String> alignment = Sets.newHashSet(qs.get("en1").asResource().getURI(),
					qs.get("en2").asResource().getURI());
			alignments.add(alignment);
		}

	}

	public static void addToCluster(Map<String, Set<Integer>> clusters, String uri, Integer c) {
		Set<Integer> cs = clusters.get(uri);
		if (cs == null) {
			cs = new HashSet<>();
		}
		cs.add(c);
		clusters.put(uri, cs);
	}

	public static void dotTOPNG(String dotFile, String png) throws IOException {
		InputStream dot = new FileInputStream(new File(dotFile));
		MutableGraph g = new Parser().read(dot);
		Graphviz.fromGraph(g).width(700).render(Format.PNG).toFile(new File(png));
	}

	public static void main(String[] args)
			throws OWLOntologyCreationException, OWLOntologyStorageException, IOException {

		String folderIn = args[0];

		System.out.println("CH Corpus \n\n");
		for (double t : new double[] { 0.0, 0.1, 0.2, 0.3, 0.4 }) {
			System.out.println("Run the experiments with minimum strength set as " + t);
			analyseAlignments(folderIn
							+ "clustering-nocomments-100-alsocommswithoutsynsetframe-filtered-framesynset-analysis-withoutnone_ch.csv",
					folderIn + "nosubsumed_recursion_belowaverage_run2_filteredforclusteranalysis/communities_original_rdf",
					folderIn + "Alignments/alignments_AML.ttl",
					folderIn + "Alignments/CH_dataset_internal_classprop_alignments.ttl", folderIn,
					folderIn + "topLevelAnchestors.csv", folderIn + "framehierarchy.csv", t,false);
			System.out.println("\n\n\n\n\n\n");
		}

		System.out.println("\n\n CONF Corpus \n\n");
		for (double t : new double[] { 0.0, 0.1, 0.2, 0.3, 0.4 }) {
			System.out.println("Threshold " + t);
			analyseAlignments(folderIn + "Conf-clustering-framesynset-analysis.csv",
					folderIn + "communities-conference-forclusteranalysis/communities_original_rdf",
					folderIn + "conference-reference-alignment/conference_alignments.ttl",
					folderIn + "Alignments/CH_dataset_internal_classprop_alignments.ttl", folderIn,
					folderIn + "topLevelAnchestors.csv", folderIn + "framehierarchy.csv", t, true);
			System.out.println("\n\n\n\n\n\n");
		}

	}
}
