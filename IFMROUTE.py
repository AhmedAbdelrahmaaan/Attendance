import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering
import matplotlib.pyplot as plt

# # Step 1: Read data from CSV file
# df = pd.read_csv('Coordinates.csv')  # Replace 'coordinates.csv' with your CSV file path
#
# # Extract latitude and longitude columns
# latitude = df['Latitude'].values
# longitude = df['Longitude'].values
# coordinates = df[['Latitude', 'Longitude']].values
#
# # Step 2: Initial Clustering
# kmeans = KMeans(n_clusters=3)
# primary_clusters = kmeans.fit_predict(coordinates)
#
# # Step 3: Hierarchical Clustering
# hierarchical_clustering = AgglomerativeClustering(n_clusters=3, linkage='average')
# hierarchical_clusters = hierarchical_clustering.fit_predict(coordinates)
#
# # Visualize the initial clusters
# plt.scatter(longitude, latitude, c=primary_clusters, cmap='viridis')
# plt.title("Primary Clusters")
# plt.xlabel("Longitude")
# plt.ylabel("Latitude")
# plt.show()
# df['Primary_Cluster'] = primary_clusters
# df['hierarchical_clusters'] = hierarchical_clusters
# df.sort_values(by='Primary_Cluster',inplace=True)
# df.reset_index(inplace=True)
# # Visualize the hierarchical clusters
# plt.scatter(longitude, latitude, c=hierarchical_clusters, cmap='viridis')
# plt.title("Hierarchical Clusters")
# plt.xlabel("Longitude")
# plt.ylabel("Latitude")
# plt.show()
#
#
# # Step 4: Determine Number of Subclusters
# # In this example, you can manually choose a level in the tree to create subclusters.
#
# # Step 5: Subcluster Formation
# # For each primary cluster, you can perform K-means clustering again.
# primary_to_subcluster = []
# for primary_cluster_id in range(3):  # Replace 3 with the number of primary clusters
#     # mask = primary_clusters == primary_cluster_id
#     # print(mask,df)
#     sliced_df = df[df['Primary_Cluster'] == primary_cluster_id]
#     subcluster_data = sliced_df[['Latitude', 'Longitude']]
#     kmeans_subcluster = KMeans(n_clusters=6)  # You can change the number of subclusters
#     subcluster_labels = kmeans_subcluster.fit_predict(subcluster_data)
#     primary_to_subcluster.extend(list(subcluster_labels))
#     # df[f'hierarchical_clusters{primary_cluster_id}'] = subcluster_labels
#     # Visualize the subclusters within a primary cluster
#     print(subcluster_data["Longitude"])
#     plt.scatter(subcluster_data["Longitude"], subcluster_data["Latitude"], c=subcluster_labels, cmap='viridis')
#     plt.title(f"Subclusters in Primary Cluster {primary_cluster_id}")
#     plt.xlabel("Longitude")
#     plt.ylabel("Latitude")
#     plt.show()
#     # subcluster_data = df[mask]
#     # primary_to_subcluster[primary_cluster_id] = subcluster_labels[:len(subcluster_data)]
#
# print(primary_to_subcluster)
# df['Subcluster'] = primary_to_subcluster
# df.to_excel("finalres.xlsx")

def IFMROUTE(df,N_Routes,working_days):
    latitude = df['latitude'].values
    longitude = df['longitude'].values
    coordinates = df[['latitude', 'longitude']].values
    kmeans = KMeans(n_clusters=N_Routes)
    primary_clusters = kmeans.fit_predict(coordinates)
    df['Route'] = primary_clusters
    df.sort_values(by='Route', inplace=True)
    df.reset_index(inplace=True)
    primary_to_subcluster = []
    for primary_cluster_id in range(N_Routes):  # Replace 3 with the number of primary clusters
        # mask = primary_clusters == primary_cluster_id
        # print(mask,df)
        sliced_df = df[df['Route'] == primary_cluster_id]
        subcluster_data = sliced_df[['latitude', 'longitude']]
        kmeans_subcluster = KMeans(n_clusters=len(working_days))  # You can change the number of subclusters
        subcluster_labels = kmeans_subcluster.fit_predict(subcluster_data)
        primary_to_subcluster.extend(list(subcluster_labels))

    df['working_Days'] = primary_to_subcluster

    return df