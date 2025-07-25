'''
usage:
vcf_file=../data/HG002_exon.vep.vcf.gz
kg_path=../db/kg.csv
ref_fai=../db/GCA_000001405.15_GRCh38_no_alt_analysis_set.ercc.fa.fai
python $code --vcf_file $vcf_file --kg_path $kg_path --ref_fai $ref_fai

input VCF with VEP annotation:
Format: Uploaded_variation|Location|Allele|Gene|Feature|Feature_type|Consequence|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|IMPACT|SYMBOL
'''

from vep import analyze_haplotypes, group_gene_ps
from primeKG import query_primeKg
from visualize_gene_pathway_disease_phenotype import plot_graph
import argparse
import subprocess
import os

parser = argparse.ArgumentParser()
parser.add_argument("--vcf_file", type=str, required=True)
parser.add_argument("--kg_path", type=str, required=True)
parser.add_argument("--ref_fai", type=str, required=True)

args = parser.parse_args()
vcf_file = args.vcf_file
kg_path = args.kg_path
REF_FAI = args.ref_fai

def get_chrom_dict():
    chrom_dict = {}

    with open(REF_FAI, 'r') as f:
        for line in f:
            chrom, end, x, y, z = line.strip().split('\t')
            chrom_dict[chrom] = int(end)
    
    return chrom_dict

if __name__ == "__main__":
    # chrom, start, end = "22", 1, 26466075
    output_path = os.path.join('results')
    subprocess.call(f'mkdir -p {output_path}', shell=True)

    chrom_dict = get_chrom_dict()

    chrom_list = [f'chr{chr}' for chr in range(1,23)] +['chrX']
    gene_names = []

    ## all chr
    for chrom in chrom_list:
        end = chrom_dict[chrom]
        hap1_results, hap2_results = analyze_haplotypes(vcf_file, chrom, 1, end)
        hap1_dict, hap2_dict, genes = group_gene_ps(hap1_results, hap2_results, chrom, 1, end)
        gene_names.extend(genes)

    ##  query KG, plot network, save to ../results
    query_primeKg(gene_names, kg_path)
    plot_graph()