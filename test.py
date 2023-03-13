from google.cloud import storage
import pyarrow as pa
import pyarrow.parquet as pq
import gcsfs



# create a client object
client = storage.Client(project="level-gizmo-376804")

# specify the bucket you want to connect to
bucket_name = "test1-openwpm-bucket"
bucket = client.get_bucket(bucket_name)

# list all the blobs in the bucket
# blobs = list(bucket.list_blobs())
# for blob in blobs:
#     print(blob.name)

fs = gcsfs.GCSFileSystem(project='level-gizmo-376804',
                         token='level-gizmo-376804-87d4e9c8fb8d.json', access="read_write")
url = 'test1-openwpm-bucket/02-04-2023-StorageControllerTest-1/visits/http_requests'
data = pq.ParquetDataset(url, use_legacy_dataset=False, filesystem=fs)
reqs = data.read_pandas().to_pandas()
# print(reqs)
print(reqs.head())
total_sites = reqs['top_level_url'].nunique()
print(total_sites)