import os
import time

start = time.time()
os.system(r"python process_docs.py -in ~/train_texts/retractedErrorData -out "
          r"~/GROBID_processed/RetractedErrorData -m generate-train -csv ~/output -lr 0-0.3")
os.system(r"python process_docs.py -in ~/train_texts/replicationProject/FALSE -out "
          r"~/GROBID_processed/ReplicationProject/FALSE -m generate-train -csv ~/output "
          r"-l 0")
os.system(r"python process_docs.py -in ~/train_texts/replicationProject/TRUE -out "
          r"~/GROBID_processed/ReplicationProject/TRUE -m generate-train -csv ~/output -l 1")
os.system(r"python process_docs.py -in ~/train_texts/publishPre -out "
          r"~/GROBID_processed/PublishPre -m generate-train -csv ~/output -lr 0.7-1")
end = time.time()

print("Time taken: ", end-start)