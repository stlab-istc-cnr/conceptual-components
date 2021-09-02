package odpd;

import java.util.List;

public class Cluster {

	private String id, name, description, img;
	private List<WeightedSpecialization> superClusters;
	private List<Community> communities;

	public Cluster(String id, String name, String description, String img, List<WeightedSpecialization> superClusters, List<Community> communities) {
		super();
		this.id = id;
		this.name = name;
		this.description = description;
		this.img = img;
		this.superClusters = superClusters;
		this.communities = communities;
	}

	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getImg() {
		return img;
	}

	public void setImg(String img) {
		this.img = img;
	}

	public List<WeightedSpecialization> getSuperClusters() {
		return superClusters;
	}

	public void setSuperClusters(List<WeightedSpecialization> superClusters) {
		this.superClusters = superClusters;
	}

	public List<Community> getCommunities() {
		return communities;
	}

	public void setCommunities(List<Community> communities) {
		this.communities = communities;
	}
	
	
	

}
