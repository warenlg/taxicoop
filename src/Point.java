import java.util.List;
import java.lang.Math;

/**
 * <p>Point est la classe représentant les croisements de la carte</p>
 * <p>Chaque Point comprend:
 * <ul>
 * <li>Un nom.</li>
 * <li>une position en longitude et latitude.</li>
 * <li>Une liste de voisins.</li>
 * </ul>
 * 
 * @author Lucas Lelievre
 * @version 1.0
 *
 */
public class Point {
	/**
	 * Le nom du point, non modifiable.
	 */
	private String name;
	
	/**
	 * Latitude du point, non modifiable.
	 */
	private double latitude;//TODO choisir unite
	
	/**
	 * Longitude du point, non modifiable.
	 */
	private double longitude;//TODO choisir unite
	
	/**
	 * liste des voisins du point;
	 */
	private List<Point> voisin;
	
	/**
	 * Constructeur de point.
	 * <p>on remplie la liste de voisin dans une autre methode;</p>
	 * 
	 * @param name
	 * 		nom du point
	 * 
	 * @param latitude
	 * 		latitude du point
	 * 
	 * @param longitude
	 * 		longitude du point
	 */
	public Point(String name, double latitude, double longitude){
		this.name = name;
		this.latitude = latitude;
		this.longitude = longitude;
		this.voisin = null;
	}
	
	/**
	 * rend deux elements voisins en les ajoutant dans la liste de voisin de l'autre
	 * @param p1
	 * @param p2
	 */
	public void makeVoisin(Point p1, Point p2){
		p1.voisin.add(p2);
		p2.voisin.add(p1);
	}
	
	/**
	 * Retourne le nom du point.
	 * 
	 * @return name
	 */
	public String getName() {
		return name;
	}
	
	/**
	 * Retourne la longitude du point.
	 * 
	 * @return longitude
	 */
	public double getLongitude() {
		return longitude;
	}
	
	/**
	 * Retourne la latitude du point.
	 * 
	 * @return latitude
	 */
	public double getLatitude() {
		return latitude;
	}
	
	/**
	 * Retourne la liste des voisins du point.
	 * 
	 * @return voisin
	 */
	public List<Point> getVoisin() {
		return voisin;
	}
	
	/**
	 * 
	 * @param destination
	 * @return
	 */
	public double getDistance(Point destination){
		return Math.sqrt(Math.pow(this.longitude-destination.longitude,2.0)+Math.pow(this.latitude-destination.latitude,2.0));//TODO remplacer par plus court chemin
	}
	
	/**
	 * 
	 * @param destination
	 * @return
	 */
	public double getTime(Point destination){
		return getDistance(destination);//TODO mettre formule de calcul et changer en type long
	}
	
	/**
	 * 
	 * @param destination
	 * @return
	 */
	public double getCost(Point destination) {
		return this.getTime(destination);//TODO mettre la vrai formule de calcul de cout
	}
}
