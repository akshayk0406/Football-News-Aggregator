#include<cstdio>
#include<iostream>
#include<algorithm>
#include<cmath>
#include<vector>
#include<string>
#include<set>
#include<map>

using namespace std;
typedef pair<int,int> ii;
typedef pair< ii, float > fii; //movie-id,user-id,rating
typedef pair< float,int > dii;

/*
Implementing Recommendation Engine using collabrative filtering
Input is sparse and is stored in CSR format
*/

/*
Structure for storing input in sparse format
*/
struct csr
{
	int *users;
	int *movies;
	float *values;
	
	int total_users;
	int total_movies;
	int non_zeros;
};

/*
Custom compare function to sort input file based on user-id
*/
bool mycmp(fii a,fii b)
{
	if(a.first.second == b.first.second) return a.first.first < b.first.first;
	return a.first.second < b.first.second;
}

/*
Reading the input
*/
void readInput(vector< fii > &inp,char *fname)
{
	FILE *fp = fopen(fname,"r");
	if(!fp) return;
	fii P;
	while(fscanf(fp,"%d,%d,%f",&P.first.first,&P.first.second,&P.second)!=EOF) inp.push_back(P);
	fclose(fp);
}

/*
Keeping track of user-id and movie-id i.e creating mapping for user-id from 0 to n-1 and for movie-id from 0 to m-1
*/
void mapData(map<int,int> &user_map,map<int,int> &movie_map,vector< fii > &train)
{
	int movies  = 0;
	int users = 0;
	
	for(int i=0;i<train.size();i++)
	{
		if(movie_map.find(train[i].first.first) == movie_map.end()) {movie_map[train[i].first.first] = movies;movies = movies+1;}
		if(user_map.find(train[i].first.second) == user_map.end()) {user_map[train[i].first.second] = users;users = users+1;}
	}
}

void printCSR(struct csr *csr_data)
{
	for(int i=0;i<csr_data->total_users;i++)
	{
		for(int j=csr_data->users[i];j<csr_data->users[i+1];j++)
			printf("%d %.6f\n",csr_data->movies[j],csr_data->values[j]);
		break;
	}	
}

/*
Normalizing user vector. Needed for computing dot product between two user-vectors
*/
vector< float > computeNormalizingFactor(struct csr *csr_data)
{
	vector< float > res;
	for(int i=0;i<csr_data->total_users;i++)
	{
		float csum = 0;
		for(int j=csr_data->users[i];j<csr_data->users[i+1];j++) csum = csum + csr_data->values[j]*csr_data->values[j];
		res.push_back(sqrt(csum));
	}
	return res;
}

/*
Normalzing user rating i.e subtracting rating given to movie with average user rating 
*/
vector< float > Normalize(struct csr *csr_data)
{
	vector< float > avg_user_rating;
	for(int i=0;i<csr_data->total_users;i++)
	{
		float csum = 0;
		for(int j=csr_data->users[i];j<csr_data->users[i+1];j++) csum = csum + csr_data->values[j];
		csum = csum/(csr_data->users[i+1] - csr_data->users[i]); 
		avg_user_rating.push_back(csum);
		for(int j=csr_data->users[i];j<csr_data->users[i+1];j++) csr_data->values[j] = csr_data->values[j] - csum; 
	}
	return avg_user_rating;
}

/*
Make prediction. Fing """neigh""" similar users to given user and returing avg of rating for the movie rated by those users
*/
float predict(int user,int movie,float avg_user_rating,struct csr *csr_data,vector< dii > &similarity)
{
	float rating = 0.0;
	int raters = 0;

	for(int i=0;i<similarity.size();i++)
	{
		for(int j=csr_data->users[similarity[i].second];j<csr_data->users[similarity[i].second+1];j++)
		{
			if(csr_data->movies[j] == movie)
			{
				rating = rating + csr_data->values[j];
				raters = raters + 1;
			}
		}
	}
	if( 0 == raters ) return avg_user_rating;
	return avg_user_rating + (rating/raters);
}

/*
Computing similarity between all-pair users
*/
vector< vector< dii >  > computeSimilarity(struct csr *csr_data,vector< float > &norms,int neigh)
{
	vector< vector< dii > > res;
	int p1 = 0;
	int p2 = 0;
	int q1 = 0;
	int q2 = 0;	
	float sum = 0.0;

	for(int k=0;k<csr_data->total_users;k++)
	{
		p1 = csr_data->users[k];
		p2 = csr_data->users[k+1];
		vector< dii > ans;
		for(int i=0;i<csr_data->total_users;i++)
		{
			if(i==k) continue;
			q1 = csr_data->users[i];
			q2 = csr_data->users[i+1];
			sum = 0.0;
			while(p1 < p2 && q1 < q2)
			{
				if(csr_data->movies[p1] ==csr_data->movies[q1])
				{
					sum = sum + csr_data->values[p1] * csr_data->values[q1];
					p1++;
					q1++;
				}
				else if(csr_data->movies[p1] < csr_data->movies[q1]) p1++;
				else q1++;
			}
			sum = sum/norms[i];
			sum = sum/norms[k];
			ans.push_back(make_pair(sum,i));
		}
		sort(ans.begin(),ans.end());
		ans.resize(neigh);
		res.push_back(ans);
	}
	return res;
}

/*
Creating CSR matrix for fast processing 
*/

void constructCSR(struct csr *csr_data,vector< fii > &train,map<int,int> &user_map,map<int,int> &movie_map)
{
	mapData(user_map,movie_map,train);

	csr_data->users 		= (int *)calloc(user_map.size()+1,sizeof(int));
	csr_data->movies  		= (int *)calloc(train.size()+1,sizeof(int));
	csr_data->values    	= (float *)calloc(train.size()+1,sizeof(float));
	csr_data->non_zeros 	= (int)train.size();
	csr_data->total_users 	= user_map.size();
	csr_data->total_movies  = movie_map.size();

	int rowptr = 0;
	int pre = -1;

	for(int i=0;i<train.size();i++)
	{
		if(train[i].first.second != pre )
		{	
			csr_data->users[rowptr] = i;
			rowptr = rowptr + 1;
		}
		
		pre = train[i].first.second;
		csr_data->movies[i] = train[i].first.first;
		csr_data->values[i] = train[i].second;
	}
	csr_data->users[rowptr] = train.size();
}

int main(int argc,char **argv)
{
	int neigh = 10;
	vector< fii > train;
	vector< fii > test;

	readInput(train,argv[1]);
	readInput(test,argv[2]);
	if(argc>=5) neigh = atoi(argv[4]);

	sort(train.begin(),train.end(),mycmp);
	puts("Input Read!!!");
	
	map<int,int> user_map;
	map<int,int> movie_map;
	
	struct csr csr_data;
	constructCSR(&csr_data,train,user_map,movie_map);
	puts("Constructed CSR!!!!");
	vector< float > avg_user_rating = Normalize(&csr_data);
	puts("Avergae User Rating !!!");
	vector< float > norms = computeNormalizingFactor(&csr_data);
	puts("Normalizing User vector");
	vector< vector< dii > > similarity = computeSimilarity(&csr_data,norms,neigh);
	puts("Computing Similarity");

	float rmse = 0.0;
	float prediction = 0.0;
	
	FILE *fp = fopen(argv[3],"w");
	for(int i=0;i<test.size();i++) 
	{
		prediction = predict(test[i].first.second,test[i].first.first,avg_user_rating[user_map[test[i].first.second]],&csr_data,similarity[user_map[test[i].first.second]]);
		rmse = rmse + ((prediction - test[i].second)*(prediction-test[i].second));
		fprintf(fp,"%d,%d,%.3f\n",test[i].first.first,test[i].first.second,prediction);
	}
	fclose(fp);
	rmse = rmse/test.size();
	rmse = sqrt(rmse);
	printf("RMSE is %.6f\n",rmse);
	return 0;
}
