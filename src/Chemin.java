import java.util.ArrayList;
import java.util.HashMap;

/**
 * 
 */

/**
 * <p>Chemin est la classe représentant les chemins pris par les taxis</p>
 * <p> un chemin comprend juste une liste de Noeud</p>
 * @author Lucas Lelievre
 * @version 1.0
 */
public class Chemin {
	
	/**
	 * Liste des noeuds du chemin
	 */
	private ArrayList<Noeud> noeuds;
	
	/**
	 * Constructeur de Chemin.
	 * <p> à sa construction la liste de noeuds est vide</p>
	 */
	public Chemin() {
		this.noeuds = null;
	}
	
	/**
	 * retourne la taille du chemin
	 * 
	 * @return
	 */
	public int size(){
		return this.noeuds.size();
	}
	/**
	 * retourne le nombre de reservations sur ce chemin
	 * 
	 * @return 
	 */
	public int getNbReservations(){
        return this.size()/2;
    }
	
	/**
	 * retourne la position du Noeud d'indice i
	 * @param i
	 * @return
	 */
	public Point getPoint(int i){
		return noeuds.get(i).getPosition();
	}
	
	/**
	 * retourne le noeud d'indice i
	 * @param i
	 * @return
	 */
	public Noeud getNoeud(int i){
		return noeuds.get(i);
	}
	
	/**
	 * retire le noeud d'indice i
	 * @param i
	 */
	public void removeNoeud(int i){
		noeuds.remove(i);
	}
	
	/**
	 * retourne la reservation du point d'indice i
	 * @param i
	 * @return
	 */
	public Reservation getReservation(int i){
		return noeuds.get(i).reservation;
	}
	
	/**
	 * retourne la liste des prix par reservation
	 * @return 
	 */
	public HashMap<Reservation, Double> getCosts(){
		
		int i;
		HashMap<Reservation, Double> costs = new HashMap<Reservation,Double>();
		
		for(i = 0; i < noeuds.size(); i++){
			
			/* 
			 * si le noeud d'indice i est l'origine d'une reservation on parcourt les noeuds suivants jusqu'a 
			 * la destination de la reservation en additionnant les prix du trajet entre chaque noeuds du chemin.
			 */
			if(noeuds.get(i).isOrigine == true){ 
				int j = i+1;
				
				/*
				 * on verifie d'abord si le noeuds suivant est la destination
				 */
				if(getReservation(i)== getReservation(j) && noeuds.get(j).isOrigine == false){
					costs.put(getReservation(i), getPoint(i).getCost(getPoint(j)));
					
				}
				/*
				 * sinon on parcours la liste jusqu'a la destination ou la fin de la liste
				 */
				else {
					double cost = getPoint(i).getCost(getPoint(j));
					while (getReservation(i) != getReservation(j) && j < noeuds.size()) {
						cost = cost + getPoint(j).getCost(getPoint(j+1));
					}
					//TODO erreur si on arrive à la fin sans avoir trouvé la destination
					costs.put(getReservation(i), cost);
				}
			}
		}
		
		return costs;
	}
	
	/**
	 * retourne la liste des temps de trajet par reservation
	 */
	public HashMap<Reservation,Long> getTimes(){
		
		// fonctionne comme Chemin.getCosts() mais avec les temps
		int i;
		HashMap<Reservation, Long> times = new HashMap<Reservation,Long>();
		
		for(i = 0; i < noeuds.size(); i++){
			
			/* 
			 * si le noeud d'indice i est l'origine d'une reservation on parcourt les noeuds suivants jusqu'a 
			 * la destination de la reservation en additionnant les temps de trajet entre chaque noeuds du chemin.
			 */
			if(noeuds.get(i).isOrigine == true){ 
				int j = i+1;
				
				/*
				 * on verifie d'abord si le noeuds suivant est la destination
				 */
				if(getReservation(i)== getReservation(j) && noeuds.get(j).isOrigine == false){
					times.put(getReservation(i), getPoint(i).getTime(getPoint(j)));
					
				}
				/*
				 * sinon on parcours la liste jusqu'a la destination ou la fin de la liste
				 */
				else {
					long time = getPoint(i).getTime(getPoint(j));
					while (getReservation(i) != getReservation(j) && j < noeuds.size()) {
						time = time + getPoint(j).getTime(getPoint(j+1));
					}
					//TODO erreur si on arrive à la fin sans avoir trouvé la destination
					times.put(getReservation(i), time);
				}
			}
		}
		return times;
	}
	
	/**
	 * insertion d'un Noeud dans noeuds à l'indice i
	 */
	public void insertionNoeud(int i, Noeud n) {
		noeuds.add(i, n);
	}
	
	/**
	 * insert l'origine de r derrière a et sa destination derrière b
	 * @param r
	 * @param a
	 * @param b
	 */
	public void insertionReservation(Reservation r, int a, int b){
		Noeud origine = new Noeud(r,true);
		Noeud destination = new Noeud(r, false);
		insertionNoeud(a+1, origine);
		insertionNoeud(b+1, destination);
	}
	/**
	 * supprime les noeuds de la reservation r dans noeuds
	 */
	public void retraitReservation(Reservation r) {
		int i;
		for(i=0; i<noeuds.size(); i++){
			if(getReservation(i) == r){
				noeuds.remove(i);
			}
		}
	}
}

/**
 * <p>noeud est la classe représentant les points du chemin du taxi </p>
 * <p>chaque noeud comprend:
 * <ul>
 * <li> Un lien vers la reservation dont il vient</li>
 * <li> Un booléen pour savoir si c'est l'origine ou la destination de la reservation </li>
 * <li>Un Point qui indique sa position</li>
 * </ul>
 */
class Noeud {
	
	/**
	 * booléen pour savoir si le Noeud est l'origine ou la destination de sa reservation.
	 */
	public boolean isOrigine;
	
	/**
	 * La reservation dont viens le Noeud.
	 */
    public Reservation reservation;
    
    /**
     * constructeur de Noeud
     * @param reservation
     * @param isOrigine
     */
    public Noeud(Reservation reservation, boolean isOrigine){
        this.isOrigine = isOrigine;
        this.reservation = reservation;
    }
    
    public Point getPosition(){
        if(isOrigine)
            return reservation.getOrigine();
        else
            return reservation.getDestination();
    }

    
}