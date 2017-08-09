
public class Reservation {
	private Point origine;
	private Point destination;
	private long heureDepart;
	private long heureArrive;
	private int nombrePassagers;
	private double maxCost;
	public Taxi taxi = null;
	public double coutActuel;
	
	public Reservation(Point origine, Point destination, long heureDepart, long heureArrive, int nombrePassagers){
		this.origine = origine;
		this.destination = destination;
		this.heureDepart = heureDepart;
		this.heureArrive = heureArrive;
		this.nombrePassagers = nombrePassagers;
		
		this.maxCost = origine.getCost(destination);
		this.coutActuel =this.maxCost;
	}
	
	public Point getOrigine() {
		return origine;
	}
	
	public Point getDestination() {
		return destination;
	}
	
	public long getHeureDepart() {
		return heureDepart;
	}
	
	public long getHeureArrive() {
		return heureArrive;
	}
	
	public int getNombrePassagers() {
		return nombrePassagers;
	}
	
	public double getMaxCost() {
		return maxCost;
	}
}

