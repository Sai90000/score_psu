from utilities import read_darpa_tsv, csv_writer, csv_write_field_header, csv_write_record
from grobid_client.grobid_client import run_grobid
from extractor import TEIExtractor
from p_value import extract_p_values
from collections import namedtuple
from os import listdir, rename, system, name, path, getcwd
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Pipeline - Process PDFS - Market Pre-processing")
    parser.add_argument("-in", "--pdf_input", help="parent folder that contains all pdfs")
    parser.add_argument("-out", "--grobid_out",  help="grobid output path")
    parser.add_argument("-m", "--mode", default="processFulltextDocument", help="grobid mode")
    parser.add_argument("-n", default=1, help="concurrency for service usage")
    parser.add_argument("-f", "--file", help="DARPA tsv for test")
    parser.add_argument("-csv", "--csv_out", default=getcwd(), help="CSV output path")
    parser.add_argument("-l", "--label", help="Assign y value | label for training set")

    args = parser.parse_args()

    # Debug parameters config
    args.mode = "extract-test"
    args.grobid_out = r"C:\Users\arjun\dev\GROBID_processed\test"
    args.pdf_input = r"C:\Users\arjun\dev\test\pdfs"
    args.file = r"C:\Users\arjun\dev\covid_ta3.tsv"

    # Process PDFS -> Generate XMLs and txt files
    if args.mode == "process-pdfs":
        # Change pdf names (Some PDFs have '-' instead of '_' in the names)
        for count, filename in enumerate(listdir("xyz")):
            print("Processing: ", filename, ", file number: ", count)
            new_name = filename.replace('-', '_')
            rename(args.pdf_input+'/'+filename, new_name)
            # Generate text files from PDFs
            if name == 'nt':
                command = r"C:\Users\arjun\dev\xpdf-tools-win-4.02\bin64\pdftotext {0}/".format(args.pdf_input) + \
                          filename
            else:
                command = "pdftotext {0}/{1}".format(args.pdf_input, filename)
            system(command)
        # Process PDFs to generate GROBID TEI XML
        run_grobid(args.pdf_input, args.grobid_out, args.n)

    # Generate Training data
    elif args.mode == "generate-train":
        fields = ('doi', 'title', 'num_citations', 'author_count', 'sjr', 'u_rank', 'num_hypo_tested', 'real_p',
                  'real_p_sign', 'p_val_range', 'num_significant', 'sample_size', "extend_p", "funded", "y")
        record = namedtuple('record', fields)
        record.__new__.__defaults__ = (None,) * len(record._fields)
        # CSV output file (Delete the file manually if you wish to generate fresh output, default appends
        writer = csv_writer(r"{0}/{1}".format(args.csv_out, "train.csv"), append=True)
        header = list(fields)
        if path.isfile(args.csv_out+"/train.csv"):
            csv_write_field_header(writer, header)
        # Run pipeline
        xmls = listdir(args.grobid_out)
        for xml in xmls:
            print("Processing ", xml)
            extractor = TEIExtractor(args.grobid_out + '/' + xml)
            extraction_stage = extractor.extract_paper_info()
            p_val_stage = extract_p_values(args.pdf_input + '/' + xml.replace('.tei.xml', '.txt'))
            features = dict(**extraction_stage, **p_val_stage)
            features['y'] = float(args.label)
            try:
                csv_write_record(writer, features, header)
            except UnicodeDecodeError:
                print("CSV WRITE ERROR", features["ta3_pid"])
            except UnicodeEncodeError:
                print("CSV WRITE ERROR", features["ta3_pid"])

    # Generate DARPA SCORE Test set
    elif args.mode == "extract-test":
        fields = ('ta3_pid', 'title', 'num_citations', 'author_count', 'sjr', 'u_rank', 'num_hypo_tested', 'real_p',
                  'real_p_sign', 'p_val_range', 'num_significant', 'sample_size', "extend_p", "funded")
        record = namedtuple('record', fields)
        record.__new__.__defaults__ = (None,) * len(record._fields)
        # CSV output file
        writer = csv_writer(r"{0}/{1}".format(args.csv_out, "test.csv"))
        header = list(fields)
        csv_write_field_header(writer, header)
        for document in read_darpa_tsv(args.file):
            print("Processing ", document['pdf_filename'])
            extractor = TEIExtractor(args.grobid_out + '/' + document['pdf_filename'] + '.tei.xml')
            extraction_stage = extractor.extract_paper_info()
            p_val_stage = extract_p_values(args.pdf_input + '/' + document['pdf_filename'] + '.txt', document['claim4'])
            features = dict(**extraction_stage, **p_val_stage)
            features['ta3_pid'] = document['ta3_pid']
            try:
                csv_write_record(writer, features, header)
            except UnicodeDecodeError:
                print("CSV WRITE ERROR", features["ta3_pid"])
            except UnicodeEncodeError:
                print("CSV WRITE ERROR", features["ta3_pid"])