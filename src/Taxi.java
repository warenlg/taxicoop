/**
 * 
 */

/**
 * <p>Taxi est la classe representant les taxis en circulation</p>
 * <p>Chaque taxi comprend:
 * <ul>
 * <li>Une position actuel.</li>
 * <li>Une fenetre de temps comprenant l'heure de debut et de fin de service.</li>
 * <li>Le nombre de places disponible.</li> 
 * <li>Le chemin emprunte par le taxi.</li>
 * </ul>
 * 
 * @author Lucas Lelievre
 * @version 1.0
 *
 */
public class Taxi {
	
	/**
	 * position du taxi au debut de l'iteration du GRASP.
	 */
	private Point position;
	
	/**
	 * heure de début de service du taxi, non modifiable.
	 */
	private long heureDebut;
	
	/**
	 * heure de fin de service du taxi, non modifiable.
	 */
	private long heureFin;
	
	/**
	 * nombres de sieges passagers dans le taxi, non modifiable.
	 */
	private int capacite;
	
	/**
	 * chemin suivi par le taxi.
	 */
	private Chemin chemin;
	
	/**
	 * Constructeur de nouveau Taxi.
	 * <p>a sa creation le taxi n'a pas de trajet.</p>
	 * 
	 * @param position
	 * 		Position du taxi au debutde son service.
	 * 
	 * @param heureDebut
	 * 		Heure de debut de service du taxi.
	 * 
	 * @param heureFin
	 * 		Heure de fin de service du taxi.
	 */
	public Taxi(Point position, long heureDebut, long heureFin, int capacite){
		this.position = position;
		this.heureDebut =heureDebut;
		this.heureFin = heureFin;
		this.capacite = capacite;
		this.chemin = null;
	}
	
	/**
	 * Met a jour la position du taxi.
	 * 
	 * @param position the position to set
	 */
	public void setPosition(Point position) {
		this.position = position;
	}
	
	/**
	 * Met a jour le chemin du taxi.
	 * 
	 * @param chemin the chemin to set
	 */
	public void setChemin(Chemin chemin) {
		this.chemin = chemin;
	}
	
	/**
	 * Retourne la position du taxi.
	 * 
	 * @return position
	 */
	public Point getPosition() {
		return position;
	}
	
	/**
	 * Retourne l'heure de debut de service du taxi.
	 * 
	 * @return heureDebut
	 */
	public long getHeureDebut() {
		return heureDebut;
	}
	/**
	 * retourne l'heure de fin de service du taxi.
	 * 
	 * @return heureFin
	 */
	public long getHeureFin() {
		return heureFin;
	}
	/**
	 * Retourne le nombre de places du taxi.
	 * 
	 * @return capacite
	 */
	public int getCapacite() {
		return capacite;
	}
	
	/**
	 * Retourne le chemin du taxi.
	 * 
	 * @return chemin
	 */
	public Chemin getChemin() {
		return chemin;
	}
}
