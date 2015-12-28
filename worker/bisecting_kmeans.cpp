#include<cstdio>
#include<cmath>
#include<algorithm>
#include<iostream>
#include<vector>
#include<set>
#include<map>
#include<queue>
#include<cassert>

#define MAX_ITERATIONS 100
using namespace std;

struct csr
{
	vector<int> 	documentidx;
	vector<int> 	documentid;
	vector<int> 	features;
	vector<float> 	values;
	int dim;
};

pair<int,pair<int,int> > readMetaData(char *fname)
{
	//Number of documents, max-featureid , non-zeros
	pair<int,pair<int,int> > result = make_pair(0,make_pair(0,0));
	FILE *fp = fopen(fname,"r");
	if(!fp) return result;
	
	int pre_document_id = -1;	
	int document_id 	= 0;
	int feature			= 0;
	float value			= 0.0;
	int lines			= 0;
	
	while(fscanf(fp,"%d%d%f",&document_id,&feature,&value)!=EOF)
	{
		if(pre_document_id != document_id)
			result.first	= result.first+1;
		result.second.first	= max(result.second.first,feature);
		lines				= lines+1;
		pre_document_id		= document_id;
	}
	
	fclose(fp);
	result.second.first 	= result.second.first + 1;
	result.second.second	= lines;
	return result;
}

void readData(char *fname,struct csr &input)
{
	FILE *fp = fopen(fname,"r");
    if(!fp) return;

    int pre_document_id = -1;
    int document_id     = 0;
    int feature         = 0;
    float value         = 0.0;
	int rowptr			= 0;
	int colptr			= 0;	

	while(fscanf(fp,"%d%d%f",&document_id,&feature,&value)!=EOF)
	{
		if(pre_document_id != document_id)
		{
			input.documentid[rowptr] 	= document_id;
			input.documentidx[rowptr] 	= colptr;
			rowptr						= rowptr+1;	
		}
	
		input.features[colptr]			= feature;
		input.values[colptr]			= value;
		colptr							= colptr+1;
		pre_document_id					= document_id;
	}
	input.documentidx[rowptr]			= colptr;
}

vector<int> getRequiredPartition(vector< vector<int> > &result)
{
	int max_size	= 0;
	int idx			= 0;
	for(int i=0;i<result.size();i++)
	{
		if(result[i].size() > max_size)
		{
			max_size 		= result[i].size();
			idx				= i;
		}
	}
	
	vector<int> answer		= result[idx];
	result.erase(result.begin()+idx);
	return answer;
}

pair<int,int> getinitClusters(int seed,int n)
{
	pair<int,int> answer;
	srand(seed);
	answer.first	= rand()%n;
	
	while(true)
	{
		answer.second = rand()%n;
		if(answer.second!=answer.first) break;	
	}
	return answer;
}

int clusterAssignment(int iter,struct csr &input,vector<int> &required_idx,vector< float > &c1,vector< float > &c2,vector<int> &assignment)
{
	int changes   = 0;
	float dist_c1 = 0.0;
	float dist_c2 = 0.0;
	for(int i=0;i<required_idx.size();i++)
	{
		dist_c1 	= 0.0;
		dist_c2		= 0.0;
		for(int j=input.documentidx[required_idx[i]];j<input.documentidx[required_idx[i]+1];j++)
		{
			dist_c1 = dist_c1 + input.values[j] * c1[input.features[j]];
			dist_c2 = dist_c2 + input.values[j] * c2[input.features[j]];
		}
		if(0==iter)
		{
			changes = changes+1;
			if(dist_c1>dist_c2) assignment[i] = 0;
			else assignment[i] = 1;
		}
		else
		{
			if(assignment[i] == 0 && dist_c1 < dist_c2) { assignment[i] = 1; changes = changes + 1;}
			else if(assignment[i] == 1 && dist_c1 > dist_c2) { assignment[i] = 0; changes = changes + 1;}
		}
	}
	return changes;
}

void normalizeDense(vector<float> &c)
{
	float csum = 0.0;
	for(int i=0;i<c.size();i++) csum = csum + c[i]*c[i];
	csum = sqrt(csum);
	for(int i=0;i<c.size();i++) c[i] = c[i]/csum;
}

void computeCentroids(struct csr &input,vector<int> &required_idx,vector<int> &assignment,vector< float > &c1,vector< float > &c2)
{
	c1.resize(input.dim,0.0);
	c2.resize(input.dim,0.0);
	
	int fc 	= 0;
	int sc	= 0;
	for(int i=0;i<required_idx.size();i++)
	{
		for(int j=input.documentidx[required_idx[i]];j<input.documentidx[required_idx[i]+1];j++) 
		{
			if(assignment[i] == 0) c1[input.features[j]] = c1[input.features[j]]+input.values[j];
			else c2[input.features[j]] = c2[input.features[j]] + input.values[j];
		}
		if(0==assignment[i]) fc++; else sc++;
	}
	for(int i=0;i<input.dim;i++) {c1[i] = c1[i]/fc;c2[i] = c2[i]/sc;}
	normalizeDense(c1);
	normalizeDense(c2);
}

pair< vector<int> , vector<int> > bisectingKMeans(struct csr &input,vector<int> &required_idx)
{
	//Get two centroids
	vector< float > c1(input.dim,0.0);
	vector< float > c2(input.dim,0.0);
	
	vector<int> assignment(required_idx.size(),-1);
	pair<int,int> clusterid = getinitClusters(1,required_idx.size());
	int first_doc			= required_idx[clusterid.first];
	int second_doc			= required_idx[clusterid.second];

	for(int i=input.documentidx[first_doc];i<input.documentidx[first_doc+1];i++) c1[input.features[i]] = input.values[i];
	for(int i=input.documentidx[second_doc];i<input.documentidx[second_doc+1];i++) c2[input.features[i]] = input.values[i];

	int changes				= 0;
	const int threshold 	= (0.03*(double)input.documentid.size())/100;
	for(int iter = 0 ; iter < MAX_ITERATIONS ; iter++ )
	{
		changes = clusterAssignment(iter,input,required_idx,c1,c2,assignment);
		computeCentroids(input,required_idx,assignment,c1,c2);
		if(changes<=threshold) break;	
	}
	pair< vector<int>, vector<int> > answer;
	for(int i=0;i<assignment.size();i++) if(assignment[i]==0) answer.first.push_back(required_idx[i]); else answer.second.push_back(required_idx[i]);
	return answer;
}

void normalize(struct csr &input)
{
	for(int i=0;i<input.documentid.size();i++)
	{
		float sum = 0.0;
		for(int j=input.documentidx[i];j<input.documentidx[i+1];j++) sum = sum + input.values[j] * input.values[j];
		sum = sqrt(sum);
		for(int j=input.documentidx[i];j<input.documentidx[i+1];j++) input.values[j] = input.values[j]/sum;
	}
}

void transform(struct csr &input)
{
	map<int,int> feature_map;
	for(int i=0;i<input.documentid.size();i++)
	{
		for(int j=input.documentidx[i];j<input.documentidx[i+1];j++)
		{
			if(feature_map.find(input.features[j])==feature_map.end()) feature_map[input.features[j]] = 0;
			feature_map[input.features[j]] = feature_map[input.features[j]] + 1;	
		}
	}

	for(int i=0;i<input.documentid.size();i++)
	{
		for(int j=input.documentidx[i];j<input.documentidx[i+1];j++) 
			input.values[j] = input.values[j] * log((float)input.documentid.size()/feature_map[input.features[j]]);
	}
}

float objective_function(struct csr &input,vector<int> &clusterid)
{
	vector< float > c1(input.dim,0.0);
	for(int i=0;i<clusterid.size();i++)
	{
		for(int j=input.documentidx[clusterid[i]];j<input.documentidx[clusterid[i]+1];j++) 
			c1[input.features[j]] = c1[input.features[j]]+input.values[j];
	}
	
	float score = 0.0;
	for(int i=0;i<c1.size();i++) score = score + c1[i]*c1[i];
	return sqrt(score);
}

vector<float> compute_cetroid(struct csr &input,vector<int> &clusterid)
{
	vector< float > c1(input.dim,0.0);
	for(int i=0;i<clusterid.size();i++)
	{
		for(int j=input.documentidx[clusterid[i]];j<input.documentidx[clusterid[i]+1];j++) 
			c1[input.features[j]] = c1[input.features[j]]+input.values[j];
	}

	for(int i=0;i<c1.size();i++) c1[i] = c1[i]/(int)clusterid.size();
	normalizeDense(c1);
	return c1;
}

float cluster_membership(struct csr &input,vector<float> &centroid,int member)
{
	float score = 0.0;
	for(int j=input.documentidx[member];j<input.documentidx[member+1];j++)
		score = score + input.values[j] * centroid[input.features[j]];
	return score;
}

int main(int argc,char **argv)
{
	char solution_file[] = "../data/clustering_solution.txt";
	struct csr input;
	pair<int,pair<int,int> > input_meta_data = readMetaData(argv[1]);
	
	input.documentidx.resize(input_meta_data.first+1,0);
	input.documentid.resize(input_meta_data.first,0);
	input.features.resize(input_meta_data.second.second,0);
	input.values.resize(input_meta_data.second.second,0.0);
	input.dim = input_meta_data.second.first;

	readData(argv[1],input);
	transform(input);
	normalize(input);

	int K = ((long long)input_meta_data.first*(long long)input_meta_data.second.first)/input_meta_data.second.second;
	int clusters = 1;

	vector<int> init_docid(input.documentid.size(),0);
	for(int i=0;i<input.documentid.size();i++) init_docid[i] = i;

	vector< vector<int> > result;	
	result.push_back(init_docid);	

	while(result.size() < K)
	{
		vector<int> required_idx					= getRequiredPartition(result);
		pair< vector<int> , vector<int> > partition = bisectingKMeans(input,required_idx);
		result.push_back(partition.first);
		result.push_back(partition.second);
	}	

	vector< pair<float,int> > cluster_score;
	for(int i=0;i<result.size();i++) cluster_score.push_back(make_pair(objective_function(input,result[i]),i)); 
	sort(cluster_score.begin(),cluster_score.end());
	reverse(cluster_score.begin(),cluster_score.end());

	FILE *fp = fopen(solution_file,"w");
	for(int i=0;i<cluster_score.size();i++)
	{
		vector<float> centroid 	= compute_cetroid(input,result[cluster_score[i].second]);
		vector< pair<float,int> >	cluster_doc;
		for(int j=0;j<result[cluster_score[i].second].size();j++) 
			cluster_doc.push_back(make_pair(cluster_membership(input,centroid,result[cluster_score[i].second][j]),result[cluster_score[i].second][j]));

		sort(cluster_doc.begin(),cluster_doc.end());
		reverse(cluster_doc.begin(),cluster_doc.end());

		fprintf(fp,"%.6f",cluster_score[i].first);
		for(int j=0;j<cluster_doc.size();j++) fprintf(fp,"%d ",input.documentid[cluster_doc[j].second]);
		fprintf(fp,"\n");
	}
	fclose(fp);
	return 0;
}
