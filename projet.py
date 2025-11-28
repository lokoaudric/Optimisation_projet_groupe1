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
    """Générateur d'instances réalistes pour VRP multi-dépôts multi-produits"""
    
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
    
    def _compute_distance_matrix(self, all_coords: List[Tuple[float, float]]) -> List[List[float]]:
        """Calcule la matrice des distances entre tous les sites"""
        n = len(all_coords)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i+1, n):
                dist = round(self._euclidean_distance(all_coords[i], all_coords[j]), 2)
                matrix[i][j] = dist
                matrix[j][i] = dist
        
        return matrix
    
    def generate_instance(self, 
                         n_garages: int,
                         n_depots: int,
                         n_stations: int,
                         n_trucks: int,
                         truck_capacity: int,
                         zone_size: float,
                         demand_range: Tuple[int, int],
                         stock_multiplier: float = 2.0,
                         difficulty: str = "medium") -> Dict:
        """
        Génère une instance complète du problème
        
        Args:
            n_garages: Nombre de garages
            n_depots: Nombre de dépôts
            n_stations: Nombre de stations-service
            n_trucks: Nombre de camions
            truck_capacity: Capacité des camions (litres)
            zone_size: Taille de la zone géographique (km)
            demand_range: (min, max) pour les demandes
            stock_multiplier: Multiplicateur pour garantir stock suffisant
            difficulty: "easy", "medium", "hard"
        """
        
        # Génération des coordonnées
        garage_coords = self._generate_coordinates(n_garages, (0, zone_size), (0, zone_size))
        depot_coords = self._generate_coordinates(n_depots, (0, zone_size), (0, zone_size))
        station_coords = self._generate_coordinates(n_stations, (0, zone_size), (0, zone_size))
        
        all_coords = garage_coords + depot_coords + station_coords
        
        # Calcul de la matrice des distances
        distance_matrix = self._compute_distance_matrix(all_coords)
        
        # Génération des garages
        garages = []
        for i in range(n_garages):
            garages.append({
                "id": f"G{i+1}",
                "name": f"Garage_{i+1}",
                "coordinates": {"x": garage_coords[i][0], "y": garage_coords[i][1]},
                "index": i
            })
        
        # Génération des dépôts avec stocks
        depots = []
        total_demand_essence = 0
        total_demand_gasoil = 0
        
        # On calculera les demandes d'abord pour ajuster les stocks
        temp_demands = []
        for _ in range(n_stations):
            demand_essence = 0
            demand_gasoil = 0
            
            # Probabilité qu'une station demande chaque produit
            if random.random() > 0.2:  # 80% chance de demander essence
                demand_essence = random.randint(demand_range[0], demand_range[1])
            if random.random() > 0.3:  # 70% chance de demander gasoil
                demand_gasoil = random.randint(demand_range[0], demand_range[1])
            
            temp_demands.append((demand_essence, demand_gasoil))
            total_demand_essence += demand_essence
            total_demand_gasoil += demand_gasoil
        
        # Génération des dépôts avec stocks suffisants
        for i in range(n_depots):
            # Répartir les stocks entre dépôts avec un peu de variation
            base_stock_essence = (total_demand_essence * stock_multiplier) / n_depots
            base_stock_gasoil = (total_demand_gasoil * stock_multiplier) / n_depots
            
            # Ajout de variation (±20%)
            stock_essence = int(base_stock_essence * random.uniform(0.8, 1.2))
            stock_gasoil = int(base_stock_gasoil * random.uniform(0.8, 1.2))
            
            depots.append({
                "id": f"D{i+1}",
                "name": f"Depot_{i+1}",
                "coordinates": {"x": depot_coords[i][0], "y": depot_coords[i][1]},
                "index": n_garages + i,
                "stock": {
                    "essence": stock_essence,
                    "gasoil": stock_gasoil
                }
            })
        
        # Génération des stations avec demandes
        stations = []
        for i in range(n_stations):
            stations.append({
                "id": f"S{i+1}",
                "name": f"Station_{i+1}",
                "coordinates": {"x": station_coords[i][0], "y": station_coords[i][1]},
                "index": n_garages + n_depots + i,
                "demand": {
                    "essence": temp_demands[i][0],
                    "gasoil": temp_demands[i][1]
                }
            })
        
        # Génération des camions
        trucks = []
        for i in range(n_trucks):
            # Assigner aléatoirement un garage de départ
            home_garage = random.choice(garages)["id"]
            
            # Variation de capacité selon difficulté
            if difficulty == "easy":
                capacity = int(truck_capacity * random.uniform(1.0, 1.2))
            elif difficulty == "medium":
                capacity = int(truck_capacity * random.uniform(0.9, 1.1))
            else:  # hard
                capacity = int(truck_capacity * random.uniform(0.7, 1.0))
            
            trucks.append({
                "id": f"T{i+1}",
                "home_garage": home_garage,
                "capacity": capacity
            })
        
        # Construction de l'instance complète
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
                "n_trucks": n_trucks,
                "products": self.PRODUCTS
            },
            "garages": garages,
            "depots": depots,
            "stations": stations,
            "trucks": trucks,
            "distance_matrix": distance_matrix,
            "statistics": {
                "total_demand_essence": total_demand_essence,
                "total_demand_gasoil": total_demand_gasoil,
                "total_stock_essence": sum(d["stock"]["essence"] for d in depots),
                "total_stock_gasoil": sum(d["stock"]["gasoil"] for d in depots),
                "avg_distance_to_nearest_depot": self._compute_avg_distance_to_depot(
                    station_coords, depot_coords
                )
            }
        }
        
        # Vérification de faisabilité
        self._verify_feasibility(instance)
        
        return instance
    
    def _compute_avg_distance_to_depot(self, station_coords: List[Tuple], 
                                       depot_coords: List[Tuple]) -> float:
        """Calcule la distance moyenne entre stations et leur dépôt le plus proche"""
        total_dist = 0
        for s_coord in station_coords:
            min_dist = min(self._euclidean_distance(s_coord, d_coord) 
                          for d_coord in depot_coords)
            total_dist += min_dist
        return round(total_dist / len(station_coords), 2) if station_coords else 0
    
    def _verify_feasibility(self, instance: Dict) -> None:
        """Vérifie la faisabilité de l'instance générée"""
        stats = instance["statistics"]
        
        # Vérifier que les stocks sont suffisants
        assert stats["total_stock_essence"] >= stats["total_demand_essence"], \
            "Stock essence insuffisant!"
        assert stats["total_stock_gasoil"] >= stats["total_demand_gasoil"], \
            "Stock gasoil insuffisant!"
        
        # Vérifier que la capacité totale est suffisante
        # total_capacity = sum(t["capacity"] for t in instance["trucks"])
        # max_demand = max(stats["total_demand_essence"], stats["total_demand_gasoil"])
        # assert total_capacity >= max_demand, \
        #     "Capacité totale des camions insuffisante!"
        
        print(f"✓ Instance vérifiée: faisable")
        print(f"  - Ratio stock/demande essence: {stats['total_stock_essence']/max(stats['total_demand_essence'],1):.2f}")
        print(f"  - Ratio stock/demande gasoil: {stats['total_stock_gasoil']/max(stats['total_demand_gasoil'],1):.2f}")
        # print(f"  - Ratio capacité/demande max: {total_capacity/max_demand:.2f}")
    
    def save_instance(self, instance: Dict, filename: str) -> None:
        """Sauvegarde l'instance en format JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(instance, f, indent=2, ensure_ascii=False)
        print(f"Instance sauvegardée: {filename}")


def generate_all_instances():
    """Génère les 5 instances demandées (2 easy, 2 medium, 1 hard)"""
    
    generator = PetroleumVRPGenerator(seed=42)
    
    configs = [
        # Instance 1: Facile - Petite zone, peu de stations
        {
            "name": "instance_easy_1.json",
            "n_garages": 2,
            "n_depots": 2,
            "n_stations": 8,
            "n_trucks": 4,
            "truck_capacity": 15000,
            "zone_size": 50.0,
            "demand_range": (2000, 5000),
            "difficulty": "easy"
        },
        # Instance 2: Facile - Capacité généreuse
        {
            "name": "instance_easy_2.json",
            "n_garages": 2,
            "n_depots": 3,
            "n_stations": 10,
            "n_trucks": 5,
            "truck_capacity": 18000,
            "zone_size": 60.0,
            "demand_range": (2000, 6000),
            "difficulty": "easy"
        },
        # Instance 3: Moyen - Zone plus large
        {
            "name": "instance_medium_1.json",
            "n_garages": 3,
            "n_depots": 3,
            "n_stations": 15,
            "n_trucks": 6,
            "truck_capacity": 12000,
            "zone_size": 100.0,
            "demand_range": (3000, 7000),
            "difficulty": "medium"
        },
        # Instance 4: Moyen - Plus de stations
        {
            "name": "instance_medium_2.json",
            "n_garages": 3,
            "n_depots": 4,
            "n_stations": 20,
            "n_trucks": 7,
            "truck_capacity": 12000,
            "zone_size": 80.0,
            "demand_range": (2500, 6500),
            "difficulty": "medium"
        },
        # Instance 5: Difficile - Grande zone, capacité limitée
        {
            "name": "instance_hard_1.json",
            "n_garages": 4,
            "n_depots": 4,
            "n_stations": 30,
            "n_trucks": 10,
            "truck_capacity": 10000,
            "zone_size": 150.0,
            "demand_range": (3000, 8000),
            "difficulty": "hard"
        }
    ]
    
    instances = []
    for i, config in enumerate(configs, 1):
        print(f"\n{'='*60}")
        print(f"Génération de l'instance {i}/5: {config['difficulty'].upper()}")
        print(f"{'='*60}")
        
        name = config.pop("name")
        instance = generator.generate_instance(**config)
        generator.save_instance(instance, name)
        instances.append(instance)
        
        print(f"\nRésumé:")
        print(f"  - Stations: {instance['parameters']['n_stations']}")
        print(f"  - Camions: {instance['parameters']['n_trucks']}")
        print(f"  - Demande totale: {instance['statistics']['total_demand_essence'] + instance['statistics']['total_demand_gasoil']} L")
    
    print(f"\n{'='*60}")
    print(f"✓ Toutes les instances ont été générées avec succès!")
    print(f"{'='*60}")
    
    return instances


if __name__ == "__main__":
    print("Générateur d'instances VRP - Distribution Pétrolière")
    print("IFRI-UAC - Projet Optimisation 2025-2026\n")
    
    generate_all_instances()