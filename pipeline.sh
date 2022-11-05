#!/bin/bash

run_fastqc() {
	fastqc $1.fastq.gz
	mv $1_fastqc.html $1.html
	rm $1_fastqc.zip
}

extract_quality() {
	return $( echo $(cat $1 | grep -oP '\d+\.\d+' | head -1)">90" | bc )
}

bwa index $2.fna
run_fastqc $1
bwa mem $2.fna $1.fastq.gz > $1.sam
samtools view -Sb -o $1.bam $1.sam
samtools flagstat $1.bam > $1_samtools.txt

extract_quality $1_samtools.txt
if [[ "$?" -eq 1 ]]; then
	echo "OK"
	samtools sort $1.bam > $1.sorted.bam
	/home/sescer/Desktop/freebayes -f $2.fna $1.sorted.bam > $1.vcf
else
	echo "Not OK"
fi
