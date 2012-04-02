#!/usr/bin/env python
# encoding: utf-8

import collections
import subprocess
import sys
import os
from datetime import datetime, date

def timestamp():
    currenttime = datetime.now()
    return currenttime.strftime("%b %d %H:%M:%S")

def gtf_to_attributes_dict(infn):
	'''
	Returns a dict of the attributes line of a GTF
	'''
	attrdict = collections.defaultdict(lambda : collections.defaultdict(dict))
	infile = open(infn, 'r')
	for line in infile:
		line = line.rstrip()
		linedict = {}
		values = line.split("\t")
		if (values[2] == "exon"):
			#print line
			attributes = values[8].split(";")
			del attributes[-1]
			attributes = [x.strip() for x in attributes]
			for attribute in attributes:
				attr = attribute.strip().split(" ")
				linedict[attr[0]] = attr[1].strip("\"")
			try:
				attrdict[linedict['transcript_id']]['gene_id'] = linedict['gene_id']
				attrdict[linedict['transcript_id']]['gene_name'] = linedict['gene_name']
			except KeyError():
				attrdict[linedict['transcript_id']]['gene_id'] = ""
				attrdict[linedict['transcript_id']]['gene_name'] = ""
				#print "Added to dict for ", linedict['transcript_id'], linedict['gene_id']
	infile.close()
	return attrdict

# Example GTF line
#chr3R	protein_coding	exon	380	1913	.	+	.	 gene_id "FBgn0037213"; transcript_id "FBtr0078962"; exon_number "1"; gene_name "CG12581"; transcript_name "CG12581-RA";

def prep_ref(gtffile,fastafile,output_dir):
	'''
	From a gtf and fasta, creates a BAM representation
	Requries the gtf_to_sam function in Cufflinks (Trapnell et. al)
	http://cufflinks.cbcb.umd.edu
	'''
	tmp_dir = output_dir + "/tmp/"
	print "[**   Setup   **] Making transcript to attribute lookup"
	txdict = gtf_to_attributes_dict(gtffile)
	print "[**   Setup   **] Convert GTF reference to SAM"
	subprocess.call(["gtf_to_sam", gtffile, tmp_dir + "/ref.sam"])
	#subprocess.call(["gtf_to_sam", gtffile, tmp_dir."/ref.sam"])
	subprocess.call(["samtools", "faidx", fastafile])
	fastidx = fastafile + ".fai"
	print "[**   Setup   **] Convert SAM reference to BAM"
	subprocess.call(["samtools", "view", "-o", tmp_dir + "/headered.bam", "-bt", fastidx,  tmp_dir + "/ref.sam"])
	subprocess.call(["samtools","sort",tmp_dir + "/headered.bam",tmp_dir + "/ref"])
	subprocess.call(["samtools", "index", tmp_dir + "/ref.bam"])
	subprocess.call(["rm", tmp_dir + "/headered.bam"])
	subprocess.call(["rm", tmp_dir + "/ref.sam"])
	#subprocess.call(["samtools", "view", "-o", "headered.bam", "-bt", fastidx,  tmp_dir + "/ref.sam"])
	#subprocess.call(["samtools","sort","headered.bam","ref"])
	#subprocess.call(["samtools", "index", "ref.bam"])
	#subprocess.call(["rm", "headered.bam"])
	#subprocess.call(["rm", "ref.sam"])
	return(txdict)

def sam_to_bam(samfile_prefix,fastafile,output_dir):
	'''
	From a sam file and fasta, creates a BAM
	'''
	print "[***************] Converting to BAM format"
	subprocess.call(["samtools", "faidx", fastafile])
	fastidx = fastafile + ".fai"

	mycommands = ["samtools", "view", "-o", output_dir + "/headered.bam", "-bt", fastidx,  output_dir + "/" + samfile_prefix + ".sam"]
	print "[running]", " ".join(mycommands)
	subprocess.call(mycommands)

	mycommands = ["samtools","sort",output_dir + "/headered.bam",output_dir + "/" + samfile_prefix]
	print "[running]", " ".join(mycommands)
	subprocess.call(mycommands)
	
	mycommands = ["samtools", "index", output_dir + "/" + samfile_prefix + ".bam"]
	print "[running]", " ".join(mycommands)
	subprocess.call(mycommands)
	
	mycommands = ["rm", output_dir + "/headered.bam"]
	print "[running]", " ".join(mycommands)
	subprocess.call(mycommands)

def prepare_output_dir(output_dir):
    logging_dir = output_dir + "/logs/"
    tmp_dir = output_dir + "/tmp/"

    #print >> sys.stderr, "[%s] Preparing output location %s" % (timestamp(), output_dir)
    print >> sys.stderr, "[**   Setup   **] Preparing output location: ", output_dir


    if os.path.exists(output_dir):
        pass
    else:        
        os.mkdir(output_dir)
        
    if os.path.exists(logging_dir):
        pass
    else:        
        os.mkdir(logging_dir)
        
    if os.path.exists(tmp_dir):
        pass
    else:        
        os.mkdir(tmp_dir)


if __name__ == "__main__":
    sys.exit(main())






