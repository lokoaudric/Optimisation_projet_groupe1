"""
Script principal pour l'exécution du générateur d'instances.
Utilise la classe PetroleumVRPGenerator pour créer des instances VRP 
garanties FAISABLES (le nombre de camions est suffisant).
"""

import os
from generator import PetroleumVRPGenerator

# Crée le dossier 'instances' s'il n'existe pas
if not os.path.exists("instances"):
    os.makedirs("instances")
    print("Dossier 'instances/' créé.")


def generate_all_instances():
    """Définit les configurations et génère toutes les instances."""
    
    # Initialisation du générateur avec une graine pour la reproductibilité
    generator = PetroleumVRPGenerator(seed=42)
    
    # Définition des configurations d'instances.
    # Remarque : n_trucks est maintenant ignoré dans le générateur
    # et sera CALCULÉ pour garantir la faisabilité.
    configs = [
        # Instance 1: Facile - Petite zone, faible demande
        {
            "name": "instance_easy_1.json",
            "n_garages": 2,
            "n_depots": 2,
            "n_stations": 10,
            "truck_capacity": 8000,
            "zone_size": 50.0,
            "demand_range": (1000, 3500), # Faible demande
            "difficulty": "easy"
        },
        # Instance 2: Facile - Plus de stations, toujours faisable
        {
            "name": "instance_easy_2.json",
            "n_garages": 2,
            "n_depots": 2,
            "n_stations": 15,
            "truck_capacity": 8000,
            "zone_size": 60.0,
            "demand_range": (1000, 3500), 
            "difficulty": "easy"
        },
        # Instance 3: Moyenne - Zone moyenne, demande modérée, moins de marge de camions
        {
            "name": "instance_medium_1.json",
            "n_garages": 3,
            "n_depots": 3,
            "n_stations": 20,
            "truck_capacity": 9000,
            "zone_size": 100.0,
            "demand_range": (2500, 5000), # Demande modérée
            "difficulty": "medium"
        },
        # Instance 4: Moyenne - Plus de dépôts, complexité du choix de départ
        {
            "name": "instance_medium_2.json",
            "n_garages": 3,
            "n_depots": 4,
            "n_stations": 25,
            "truck_capacity": 9000,
            "zone_size": 120.0,
            "demand_range": (2500, 5000), 
            "difficulty": "medium"
        },
        # Instance 5: Difficile - Grande zone, forte demande, n_trucks minimal (marge 0%)
        {
            "name": "instance_hard_1.json",
            "n_garages": 4,
            "n_depots": 4,
            "n_stations": 30,
            "truck_capacity": 10000,
            "zone_size": 150.0,
            "demand_range": (4000, 8000), # Forte demande
            "difficulty": "hard"
        },
         # Instance 6: Difficile - Très grande instance, n_trucks minimal (marge 0%)
        {
            "name": "instance_hard_2.json",
            "n_garages": 5,
            "n_depots": 5,
            "n_stations": 40,
            "truck_capacity": 10000,
            "zone_size": 200.0,
            "demand_range": (4000, 8000), 
            "difficulty": "hard"
        }
    ]
    
    instances = []
    print(f"\nGénération de {len(configs)} instances VRP garanties faisables.\n")
    
    for i, config in enumerate(configs, 1):
        print(f"{'='*60}")
        print(f"Génération de l'instance {i}/{len(configs)}: {config['difficulty'].upper()} - {config['name']}")
        print(f"{'='*60}")
        
        name = config.pop("name")
        instance = generator.generate_instance(**config)
        generator.save_instance(instance, name)
        instances.append(instance)
        
        print(f"\nRésumé de l'instance {name}:")
        print(f"  - Stations: {instance['parameters']['n_stations']}")
        print(f"  - Capacité Camion: {instance['parameters']['truck_capacity']} L")
        print(f"  - Demande totale Essence: {instance['statistics']['total_demand_essence']} L ({instance['statistics']['required_trucks_essence']} camions min)")
        print(f"  - Demande totale Gasoil: {instance['statistics']['total_demand_gasoil']} L ({instance['statistics']['required_trucks_gasoil']} camions min)")
        print(f"  - Camions MINIMUM requis: {instance['statistics']['min_total_required_trucks']}")
        print(f"  - Camions DISPONIBLES (n_trucks): {instance['parameters']['n_trucks']} <--- Instance FAISABLE")
        print("-"*60)
        
    print("\n\n✅ Génération de toutes les instances terminée.")


if __name__ == "__main__":
    generate_all_instances()