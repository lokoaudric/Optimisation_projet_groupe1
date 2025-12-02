"""
Générateur d'instances pour le problème VRP de distribution pétrolière
Auteur: Projet Optimisation IFRI-UAC
Format: JSON structuré
"""

import json
import random
import math
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np

class PetroleumVRPGenerator:
    """Générateur d'instances réalistes et GARANTIES FAISABLES pour VRP multi-dépôts multi-produits"""
    
    PRODUCTS = ["essence", "gasoil"]
    
    def __init__(self, seed: int = 42):
        """Initialise le générateur avec une graine aléatoire"""
        random.seed(seed)
        np.random.seed(seed)
    
    def _euclidean_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calcule la distance euclidienne entre deux points"""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def _generate_coordinates(self, n: int, x_range: Tuple[float, float], 
                            y_range: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Génère n coordonnées aléatoires dans la zone spécifiée"""
        coords = []
        for _ in range(n):
            x = random.uniform(x_range[0], x_range[1])
            y = random.uniform(y_range[0], y_range[1])
            coords.append((round(x, 2), round(y, 2)))
        return coords

    def _generate_demands(self, n_stations: int, demand_range: Tuple[int, int]) -> List[Dict[str, int]]:
        """Génère des demandes aléatoires pour chaque station et produit"""
        all_demands = []
        min_d, max_d = demand_range
        for _ in range(n_stations):
            demand = {
                "essence": random.randint(min_d, max_d),
                "gasoil": random.randint(min_d, max_d),
            }
            all_demands.append(demand)
        return all_demands

    def _calculate_required_trucks(self, total_demand: int, truck_capacity: int) -> int:
        """Calcule le nombre minimal de camions requis pour une demande totale donnée"""
        if total_demand == 0:
            return 0
        # Utiliser math.ceil pour obtenir l'entier supérieur
        return math.ceil(total_demand / truck_capacity)

    def generate_instance(self, n_garages: int, n_depots: int, n_stations: int, 
                          truck_capacity: int, zone_size: float, demand_range: Tuple[int, int],
                          difficulty: str, **kwargs) -> Dict:
        """Génère une instance complète avec toutes les données et garantit la faisabilité."""
        
        # 1. Préparation des coordonnées
        max_coord = zone_size
        x_range = (0.0, max_coord)
        y_range = (0.0, max_coord)
        
        # Coordonnées pour tous les lieux
        all_coords = self._generate_coordinates(n_garages + n_depots + n_stations, x_range, y_range)
        coords_garages = all_coords[:n_garages]
        # 2. Génération des demandes pour les stations
        station_demands = self._generate_demands(n_stations, demand_range)
        
        # 3. Calcul des demandes totales pour chaque produit
        total_demand_essence = sum(d["essence"] for d in station_demands)
        total_demand_gasoil = sum(d["gasoil"] for d in station_demands)

        # 4. GARANTIE DE FAISABILITÉ : Calculer le nombre minimal de camions requis
        req_trucks_essence = self._calculate_required_trucks(total_demand_essence, truck_capacity)
        req_trucks_gasoil = self._calculate_required_trucks(total_demand_gasoil, truck_capacity)
        
        # Le nombre minimal de camions est la somme des besoins par produit
        # Puisque 1 camion ne transporte qu'UN SEUL type de produit par tournée.
        min_total_required_trucks = req_trucks_essence + req_trucks_gasoil
        
        #generation des camions
        trucks = []
        for i in range( min_total_required_trucks):
            coords = coords_garages.pop(random.randint(0, len(coords_garages)-1))
            trucks.append({
                "id": f"D{i+1}",
                "name": f"trucks_{i+1}",
                "coordinates": {"x": coords[0], "y": coords[1]},
                "index": n_garages + i
                "capacity"
            })

        # Ajout d'une petite marge pour que le problème soit optimisable (non trivial)
        # Easy: 20% de marge
        # Medium: 10% de marge
        # Hard: 0% de marge (n_trucks = min_total_required_trucks)
        
        if difficulty == 'easy':
            # Beaucoup de ressources, problème facile
            truck_margin = 1.2
        elif difficulty == 'medium':
            # Ressources limitées, le solveur doit bien optimiser
            truck_margin = 1.1
        else: # hard
            # Nombre minimal de camions : très difficile à résoudre
            truck_margin = 1.0 
        
        n_trucks = math.ceil(min_total_required_trucks * truck_margin)
        
        # On s'assure qu'on a au moins 1 camion par produit si la demande existe
        n_trucks = max(n_trucks, 2)
        n_trucks = max(n_trucks, min_total_required_trucks)


        # 5. Construction des listes de lieux
        
        garages = []
        for i in range(n_garages):
            coords = all_coords.pop(0)
            garages.append({
                "id": f"G{i+1}",
                "name": f"Garage_{i+1}",
                "coordinates": {"x": coords[0], "y": coords[1]},
                "index": i
            })

        depots = []
        for i in range(n_depots):
            coords = all_coords.pop(0)
            depots.append({
                "id": f"D{i+1}",
                "name": f"Depot_{i+1}",
                "coordinates": {"x": coords[0], "y": coords[1]},
                "index": n_garages + i
            })
            
        stations = []
        for i in range(n_stations):
            coords = all_coords.pop(0)
            stations.append({
                "id": f"S{i+1}",
                "name": f"Station_{i+1}",
                "coordinates": {"x": coords[0], "y": coords[1]},
                "index": n_garages + n_depots + i,
                "demand": station_demands[i]
            })

        # 6. Construction de la matrice de distances
        all_sites = garages + depots + stations
        n_sites = len(all_sites)
        distance_matrix = np.zeros((n_sites, n_sites))
        
        for i in range(n_sites):
            for j in range(n_sites):
                p1 = (all_sites[i]['coordinates']['x'], all_sites[i]['coordinates']['y'])
                p2 = (all_sites[j]['coordinates']['x'], all_sites[j]['coordinates']['y'])
                distance_matrix[i, j] = round(self._euclidean_distance(p1, p2), 2)
                
        # Conversion en liste de listes pour JSON
        distance_matrix_list = distance_matrix.tolist()

        # 7. Création de l'instance finale
        instance = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "difficulty": difficulty,
                "zone_size_km": zone_size,
                "description": f"Instance {difficulty} avec {n_stations} stations"
            },
            "parameters": {
                "n_garages": n_garages,
                "n_depots": n_depots,
                "n_stations": n_stations,
                "n_trucks": n_trucks, # Nombre de camions garanti faisable
                "truck_capacity": truck_capacity,
                "products": self.PRODUCTS
            },
            "garages": garages,
            "depots": depots,
            "stations": stations,
            "distance_matrix": distance_matrix_list,
            "statistics": {
                "total_demand_essence": total_demand_essence,
                "required_trucks_essence": req_trucks_essence,
                "total_demand_gasoil": total_demand_gasoil,
                "required_trucks_gasoil": req_trucks_gasoil,
                "min_total_required_trucks": min_total_required_trucks,
                "total_trucks_available": n_trucks
            }
        }
        
        return instance

    def save_instance(self, instance: Dict, filename: str):
        """Sauvegarde l'instance générée dans un fichier JSON"""
        with open(f"instances/{filename}", 'w') as f:
            json.dump(instance, f, indent=2)

    
# --- Fin de la classe PetroleumVRPGenerator ---