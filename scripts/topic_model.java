package ltm;

import cc.mallet.topics.*;
import cc.mallet.util.*;
import cc.mallet.types.*;
import cc.mallet.types.InstanceList.CrossValidationIterator;
import cc.mallet.pipe.*;
import cc.mallet.pipe.iterator.*;

import java.util.*;
import java.util.regex.*;
import java.io.*;
import java.lang.*;
/**
The topic_model class trains multiple LDA models with 10, 20, 40, and 80 topics. First, the data is
tokenized for input, it is then modelled using LDA to yield topic distributions, which are written to file.
The data is also partitioned into training and testing sets to evaluate the topic models' perplexity scores.
**/
public class topic_model {

	public static void main(String args[]) throws Exception {
		
		// Data processing pipeline 
		ArrayList<Pipe> pipeList = new ArrayList<Pipe>();
		pipeList.add( new CharSequenceLowercase() );
		pipeList.add( new CharSequence2TokenSequence(Pattern.compile("\\p{L}[\\p{L}\\p{P}]+\\p{L}")) );
		pipeList.add( new TokenSequence2FeatureSequence() );
		pipeList.add( new TargetStringToFeatures() );
		
		InstanceList instances = new InstanceList (new SerialPipes(pipeList));
		
		Pattern compPattern = Pattern.compile("^(\\S*)[\\s,]*(\\S*)[\\s,]*(.*)$");
		
		// Corpus processed
		String fileNameLDA="data/lda_corpus.tsv";
		Reader fileReader = new InputStreamReader(new FileInputStream(new File(fileNameLDA)), "UTF-8");
		instances.addThruPipe(new CsvIterator (fileReader, compPattern,3,2,1));
	
		
		int TRAINING=0;
		int TESTING=1;
		
		int[] numTopics= {10,20,40,80};
		int numFolds = 10;
		int numModels = 1;
		int totNumTokens = 0;
		CrossValidationIterator cvList = null;
		ParallelTopicModel model = null;
		
		double[][][] perplexity = new double[numTopics.length][numModels][numFolds];
		
		for (int i=0;i<numTopics.length;i++) {
			for (int j=0;j<numModels;j++) {
				if (j==0) {
					cvList = instances.crossValidationIterator(numFolds);
					model = new ParallelTopicModel(numTopics[i]);
				}
				model.addInstances(instances);
						
				model.setBurninPeriod(250);
				model.setNumIterations(1250);
				model.estimate();

				// Write model topic distributions to file			
				model.printDocumentTopics(new File("data/model/"+j+"/"+i+"/topics"));	
				model.printTopWords(new File("data/model/"+j+"/"+i+"/top10words"),10,false);
				
				// Compute perplexity of cross-validated topic models 
				InstanceList[] nextFold = null;
				double trainloglik=0;
				double testloglik=0;
				
				for (int k=0;k<numFolds;k++) {
					if (j==0) {
						model = new ParallelTopicModel(numTopics[i]);
					}		
					ParallelTopicModel dummy = new ParallelTopicModel(numTopics[i]);
					
					
					nextFold=cvList.next();
					model.addInstances(nextFold[TRAINING]);
					dummy.addInstances(nextFold[TESTING]);
					
					model.setBurninPeriod(250);
					model.setNumIterations(1250);
					model.estimate();
					
					
					MarginalProbEstimator testEstimator=model.getProbEstimator();
					trainloglik = testEstimator.evaluateLeftToRight(nextFold[TRAINING],10,false,null);
					testloglik = testEstimator.evaluateLeftToRight(nextFold[TESTING],10,false,null);
					totNumTokens=dummy.totalTokens;
					
					perplexity[i][j][k]=Math.exp(-testloglik/totNumTokens);
					System.out.println(i+" "+j+" "+k);
					System.out.println(perplexity[i][j][k]);		
				}
			}
		}

		// Write perplexity scores to file 
		StringBuilder builder = new StringBuilder();
		for (int i=0;i<numTopics.length;i++) {
			for (int j=0;j<numModels;j++) {
				if (j==0) {
					builder.append("LDA with with "+numTopics[i]+" topics\t");
				}
				for (int k=0;k<numFolds;k++) {
					builder.append(perplexity[i][j][k]);
					if (k<numFolds-1) {
						builder.append("\t");
					}
				}
				builder.append("\n");
			}
		}
		BufferedWriter writer = new BufferedWriter(new FileWriter("data/perplexity.tsv"));
		writer.write(builder.toString());
		writer.close();

	}
}
