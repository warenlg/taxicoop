import java.util.ArrayList;
import java.util.Random;

/**
 * 
 */

/**
 * @author Lucas Lelievre
 *
 */
public class GRASP {
	
	/**
	 * liste des taxis disponibles
	 */
	public ArrayList<Taxi> taxis;
	
	/**
	 * liste desReservation non desservis
	 */
	public ArrayList<Reservation> reservations;
	
	/**
	 * solution du GRASP
	 */
	public ArrayList<Chemin> chemins;
	
	/**
	 * constructeur du GRASP.
	 * @param taxis
	 * @param reservations
	 */
	public GRASP( ArrayList<Taxi> taxis, ArrayList<Reservation> reservations){
		this.taxis = taxis;
		this.reservations = reservations;
		recupererChemin();//récupère les chemins à partir des taxis.
	}
	
	/**
	 * execution principale du GRASP,
	 * donne une solution à partis de taxis et reservations.
	 */
	public void execution(){
		
		ArrayList<ArrayList<Chemin>> solutions = new ArrayList<ArrayList<Chemin>>();// liste des différentes solutions  du GRASP
		int n = 2; //nombre d'itération du graps, TODO choisir 
		int i;
		
		for(i=0; i<n; i++){
			ArrayList<Chemin> solution = greedySolution();
			localSearch(solution);
			solutions.add(solution);
		}
		ArrayList<Chemin> solution = pathRelinking(solutions.get(0), solutions.get(1));
		localSearch(solution);
		this.chemins = solution;
		changerChemin();
	}
	
	/**
	 * Verifie que le chemin est valide
	 * @param c
	 * @return
	 */
	public boolean trajetValide(Chemin c){
		//TODO verification de validation du trajet
		
		return false;
	}
	
	/**
	 * calcule la fonction d'efficacité du chemin
	 * @param c
	 * @return
	 */
	public double trajetOptimise(Chemin c){
		//TODO fonction a maximiser page 2887 bas de la colonne 1
		
		return 0;
	}
	
	/**
	 * fonction d'insertion d'une reservation dans un chemin
	 * @param r
	 * @param c
	 */
	public void insertion(Reservation r, Chemin c){
		/*
		 * pour toutes pair (a,b) de noeuds, on place depart derrière a et arrivé derrière b
		 * calcule d'optimisation pour chaque essai
		 * choisir meilleur solution
		 */
		//TODO verifier la capacité du taxi
		
		int n = c.size();
		int a;
		int b;
		int bestOrigine = 0;
		int bestDestination = 0;
		double bestOpti = 0;
		
		for(a=0; a<n; a++){
			for(b=0; b<n; b++){
				c.insertionReservation(r, a, b);
				if(trajetValide(c)){
					double o = trajetOptimise(c);
					if(o > bestOpti){
						bestOrigine = a;
						bestDestination = b;
						bestOpti = o;
					}
				}
				c.retraitReservation(r);
			}
		}
		c.insertionReservation(r, bestOrigine, bestDestination);
	}
	
	/**
	 * calcule la fonction greedy d'une reservation dans un chemin
	 * @param r
	 * @param c
	 * @return
	 */
	public double greedyFunction(Reservation r, Chemin c){
		//TODO
		
		return 0;
	}
	
	/**
	 * récupère les chemin de taxis
	 */
	public void recupererChemin(){
		
		ArrayList<Chemin> solution = new ArrayList<Chemin>();
		int n = this.taxis.size();
		int i;
		
		for(i=0; i<n; i++){
			solution.add(this.taxis.get(i).getChemin());
		}
		this.chemins = solution;
	}
	
	/**
	 * change les chemins de taxis
	 */
	public void changerChemin(){
		
		int n = this.taxis.size();
		int i;
		
		for(i=0; i<n; i++){
			this.taxis.get(i).setChemin(this.chemins.get(i));
		}
	}
	
	/**
	 * calcule de toutes les fonctions gloutonnes pour un chemin c
	 * @param c
	 * @return
	 */
	public ArrayList<Double> gloutonnes(Chemin c){
		
		ArrayList<Double> gloutonnes = new ArrayList<Double>();
		int n = this.reservations.size();
		int i;
		
		for(i=0; i<n; i++){
			gloutonnes.add(greedyFunction(this.reservations.get(i), c));
		}
		
		return gloutonnes;
	}
	
	/**
	 * execution principale de la méthode gloutonne
	 * @return
	 */
	public ArrayList<Chemin> greedySolution(){

		ArrayList<Chemin> solution = (ArrayList<Chemin>) chemins.clone();
		ArrayList<Chemin> nonTraite =(ArrayList<Chemin>) chemins.clone();
		int n = this.chemins.size();
		int i;
		int j;
		
		for(i=0; i<n; i++){
			
			//selection aléatoire d'un chemin
			Chemin c = nonTraite.get(new Random().nextInt(n));
			Chemin k = solution.get(solution.indexOf(c));
			nonTraite.remove(nonTraite.indexOf(c));
			
			//calcul des fonctions gloutonnes
			ArrayList<Double> gloutonnes = gloutonnes(k);
			
			//creation de la liste reduite avec un critere sur le resultal de la fonction gloutonne 
			ArrayList RLC = new ArrayList();
			for(j=0; j<n; j++){
				if(gloutonnes.get(j) < 1){ //TODO definir l'intervale et le alpha(haut de la page 10)
					RLC.add(j);
				}
			}
			
			//test d'insertion des requètes de la RLC dans le chemin k
			int m = RLC.size();
			for(j=0; j<m; j++){
				int r=(int)RLC.get(new Random().nextInt(m));
				RLC.remove(RLC.indexOf(r));
				Reservation R = this.reservations.get(r);
				insertion(R, k);
				if(!trajetValide(k)){
					k.retraitReservation(R);
				}
			}
			
		}
		
		return solution;
	}
	
	/**
	 * calcule la fonction pour connaitre la qualité de la solution
	 * @param solution
	 * @return
	 */
	public double solutionOpti(ArrayList<Chemin> solution){
		//TODO
		return 0;
	}
	
	/**
	 * supprime la requete a et insert la requete b (localsearch)
	 * @param a
	 * @param b
	 * @param c
	 */
	public void remplacerRequete( Reservation a, Reservation b, Chemin c){
		c.retraitReservation(a);
		insertion(a, c);	
	}
	
	/**
	 * permutation de reservation (localsearch)
	 * @param a
	 * @param ac
	 * @param b
	 * @param bc
	 */
	public void permuterRequete(Reservation a, Chemin ac, Reservation b, Chemin bc){
		remplacerRequete(a, b, ac);
		remplacerRequete(b, a, bc);
	}
	
	/**
	 * echange la position des noeuds d'indice a et b dans c (localsearch)
	 * @param c
	 * @param a
	 * @param b
	 */
	public void permuterNoeuds(Chemin c, int a, int b){
		Noeud an = c.getNoeud(a);
		Noeud bn = c.getNoeud(b);
		c.removeNoeud(a);
		c.removeNoeud(b);
		c.insertionNoeud(a, bn);
		c.insertionNoeud(b, an);
	}
	
	/**
	 * execution principale de la recherche locale
	 * @param solution
	 */
	public void localSearch(ArrayList<Chemin> solution){
		/*TODO definir param
		 * boucle: à chaque iteration effectue trois operation pour obtenir trois solutions
		 * pour obtenir trois nouvelles solutions, on garde entre la meilleure les trois et de la solution originale
		 * opérations:
		 * enlever une requète d'une route et en mettre une autre à la place
		 * permuter deux requètes de deux routes différentes
		 * permuter deux points consécutifs d'une meme route
		 * on continue pour un nombre maximum d'itération ou
		 * jusqu'a ce qu'il n'y ai plus d'amélioration
		 */
		
	}
	
	/**
	 * execution principale du path relinking
	 * @param solution1
	 * @param solution2
	 * @return
	 */
	public ArrayList<Chemin> pathRelinking(ArrayList<Chemin> solution1, ArrayList<Chemin> solution2) {
		/*TODO definir param
		 * on prend deux solutions s1 et s2
		 * a chaque itération on effectue une opération sur s1 pour le faire ressembler plus à s2
		 * quand s1 = s2 ou qu'on atteind un nombre max d'itération, on prend la meilleur solution trouvé
		 * opérations:
		 * reservation pas servi dans s1 mais servi dans s2
		 * reservation servie dans s1 mais pas dans s2
		 * reservation servis dans différents vehicules
		 * l'opération qui améliore le plus la solution est conservé
		 */
		return null;
	}
}
