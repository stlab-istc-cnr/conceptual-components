package odpd;

public class WeightedSpecialization {
	private double strength;
	private Cluster c;

	public double getStrength() {
		return strength;
	}

	public void setStrength(double strength) {
		this.strength = strength;
	}

	public Cluster getC() {
		return c;
	}

	public void setC(Cluster c) {
		this.c = c;
	}

	public WeightedSpecialization(double strength, Cluster c) {
		super();
		this.strength = strength;
		this.c = c;
	}

}
