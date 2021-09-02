package odpd;

public class Community {

	private String name;
	private String img;
	private String communityURL;
	private String sourceOntologyURL, id, description;
	private String ontologyName;

	public Community(String id, String name, String img, String communityURL, String sourceOntologyURL,
			String description, String ontologyName) {
		super();
		this.id = id;
		this.name = name;
		this.img = img;
		this.communityURL = communityURL;
		this.sourceOntologyURL = sourceOntologyURL;
		this.description = description;
		this.ontologyName = ontologyName;

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

	public String getImg() {
		return img;
	}

	public void setImg(String img) {
		this.img = img;
	}

	public String getCommunityURL() {
		return communityURL;
	}

	public void setCommunityURL(String communityURL) {
		this.communityURL = communityURL;
	}

	public String getSourceOntologyURL() {
		return sourceOntologyURL;
	}

	public void setSourceOntologyURL(String sourceOntologyURL) {
		this.sourceOntologyURL = sourceOntologyURL;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getOntologyName() {
		return ontologyName;
	}

	public void setOntologyName(String ontologyName) {
		this.ontologyName = ontologyName;
	}

}
