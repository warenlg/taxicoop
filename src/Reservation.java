/**
 * <p>Reservation est la classe representant la reservation d'un trajet faite pas un utilisateur</p>
 * <p>Une reservation comprend:
 * <ul>
 * <li>Un point de depart et d'arrive.</li>
 * <li>Une fenetre de temps comprenant l'heure apres laquel le passager souhaite partir et l'heure avant laquel il veut arriver.</li>
 * <li>Le nombre de personnes comprises dans la reservation.</li> 
 * <li>Le cout de trajet par une methode classique (sans partage).</li>
 * <li>Le taxi sur lequel est place la reservation.</li>
 * <li>Le  cout du trajet dans le taxi partagé actuelle.</li>
 * </ul>
 * 
 * @author Lucas Lelievre
 * @version 1.0
 *
 */
public class Reservation {
	
	/**
	 * Le point de depart de la reservation, non modifiable.
	 */
	private Point origine;
	
	/**
	 * Le point d'arrive de la reservation, non modifiable.
	 */
	private Point destination;
	
	/**
	 * L'heure de depart minimum, non modifiable.
	 */
	private long heureDepart;
	
	/**
	 * L'heure d'arrive maximum, non modifiable.
	 */
	private long heureArrive;
	
	/**
	 * Nombre de passagers de la reservation, non modifiable.
	 */
	private int nombrePassagers;
	
	/**
	 * Le cout du trajet non partage, non modifiable.
	 */
	private double maxCost;
	
	/**
	 * Le Taxi assigne a la reservation.
	 */
	private Taxi taxi;
	
	/**
	 * Cout du trajet dans le taxi actuel.
	 */
	private double coutActuel;
	
	/**
	 * Constructeur de Reservation
	 * <p> A la construction d'une Reservation on calcul maxCost, taxi est null et coutActuel 
	 * vaut maxCost car la reservation n'est pas encore dans un taxi partage.</p>
	 * 
	 * @param origine
	 * 		Le point de départ.
	 * 
	 * @param destination
	 * 		Le point d'arrive.
	 * 
	 * @param heureDepart
	 * 		L'heure de départ minimum.
	 * 
	 * @param heureArrive
	 * 		l'heure d'arrive maximum.
	 * 
	 * @param nombrePassagers
	 * 		le nombre de passagers de  la reservation.
	 * 
	 */
	public Reservation(Point origine, Point destination, long heureDepart, long heureArrive, int nombrePassagers){
		this.origine = origine;
		this.destination = destination;
		this.heureDepart = heureDepart;
		this.heureArrive = heureArrive;
		this.nombrePassagers = nombrePassagers;
		
		this.maxCost = origine.getCost(destination);
		
		this.taxi = null;
		this.coutActuel =this.maxCost;
	}
	
	/**
	 * Retourne le point de depart de la reservation.
	 * 
	 * @return origine
	 */
	public Point getOrigine() {
		return origine;
	}
	
	/**
	 * Retourne le point d'arrive de la reservation.
	 * @return destination
	 */
	public Point getDestination() {
		return destination;
	}
	
	/**
	 * Retourne l'heure de depart de la reservation.
	 * 
	 * @return heureDepart
	 */
	public long getHeureDepart() {
		return heureDepart;
	}
	
	/**
	 * Retourne l'heure d'arrive de la reservation.
	 * 
	 * @return heureArrive
	 */
	public long getHeureArrive() {
		return heureArrive;
	}
	
	/**
	 * Retourne le nombre de passagers de la reservation.
	 * 
	 * @return nombrePassagers
	 */
	public int getNombrePassagers() {
		return nombrePassagers;
	}
	
	/**
	 * Retourne le cout du trajet non partage
	 * 
	 * @return maxCost
	 */
	public double getMaxCost() {
		return maxCost;
	}
	
	/**
	 * Retourne le taxi charge de la reservation.
	 * 
	 * @return taxi
	 */
	public Taxi getTaxi() {
		return taxi;
	}
	
	/**
	 * Retourne le cout de la reservation dans le taxi actuel.
	 * 
	 * @return coutActuel
	 */
	public double getCoutActuel() {
		return coutActuel;
	}
	
	/**
	 * Met a jour le taxi charge de la reservation.
	 * 
	 * @param taxi the taxi to set
	 */
	public void setTaxi(Taxi taxi) {
		this.taxi = taxi;
	}
	
	/**
	 * Met a jour le cout du trajet dans le taxi actuel.
	 * 
	 * @param coutActuel the coutActuel to set
	 */
	public void setCoutActuel(double coutActuel) {
		this.coutActuel = coutActuel;
	}
}

