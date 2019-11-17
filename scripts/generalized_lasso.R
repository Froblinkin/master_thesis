# Perform lasso logistic regression on interval target variable tasks 

rm(list = ls())

library(usdm)
library(stargazer)
library(glmnet)
library(caret)

set.seed(1)

# Set up control variables 
control_df <- function(df,dummy){
  df$reissue<-as.factor(df$reissue)
  df$crossover<-as.factor(df$crossover)
  df$time<-as.factor(df$time)
  df$success<-as.factor(df$success)
  df$long<-as.factor(df$long)
  df$genre<-as.factor(df$genre)
  if (dummy==FALSE){
    df$key<-as.factor(df$key)
    df$mode<-as.factor(df$mode)
    df$time_signature<-as.factor(df$time_signature)
  }
  return(df)
}

# Build DataFrame for modelling 
build_df <- function(df,target_var,hit=list(),miss=list(),dummy){
  df<-unique(df)
  # Remove metadata features 
  if (dummy==1){
      df<-df[-c(match("reissue",colnames(df)),match("success",colnames(df)),match("genre",colnames(df)),match("crossover",colnames(df)),match("time",colnames(df)),match("long",colnames(df)))]
      v<-vifstep(df[-c(match("interval",colnames(df)),match("align",colnames(df)),match("X0",colnames(df)))],4)
      df$key<-as.factor(df$key)
      df$mode<-as.factor(df$mode)
      df$time_signature<-as.factor(df$time_signature)
  }
  # Keep metadata features 
  else{
    v<-vifstep(df[-c(match("interval",colnames(df)),match("align",colnames(df)),match("X0",colnames(df)))],4)
    df<-control_df(df,FALSE)
  }

  # Relevel hits and flops
  df_colnames<-colnames(exclude(df,v))
  df<-df[c(df_colnames,target_var)]
  agr_hit=as.logical((df[target_var][,1]==-1))
  for (h in hit){
    agr_hit=agr_hit+as.logical((df[target_var][,1]==h))
  }
  
  agr_miss=as.logical((df[target_var][,1]==-1))
  for (m in miss){
    agr_miss=agr_miss+as.logical((df[target_var][,1]==m))
  }
  
  df[as.logical(agr_miss),][target_var][,1]=0
  df[as.logical(agr_hit),][target_var][,1]=1
  df<-df[as.logical((agr_miss+agr_hit)),]
  df[target_var][,1]<-as.factor(df[target_var][,1])
  return(df)
}

# finish writing this method up
fit_lasso <- function(df,target_var,lambda=NULL) {
  Y=df[target_var][,1]
  X=model.matrix(~.,df[-c(match(target_var,colnames(df)))])
  X<-X[,-1]
  if(!is.null(lambda)){
    penalty_fit <-glmnet(x = X, y = Y, alpha = 1, lambda = lambda,family="binomial")
    return(penalty_fit)
  }
  crossval <-  cv.glmnet(x = X, y = Y,alpha=1,family="binomial",nfolds=10)
  penalty <- crossval$lambda.1se #optimal lambda
  penalty_fit <-glmnet(x = X, y = Y, alpha = 1, lambda = penalty,family="binomial") #estimate the model with that
  return(penalty_fit)
}
  
  
# Read in data 
path_tm20="thesis/data/final/model1_data.tsv"
df_tm20=read.table(file=path_tm20,sep='\t',header=TRUE)

# Time tasks initialized 
time_hit_61=c(2,3,4)
time_miss_61=0
df_time_61<-build_df(df_tm20,"interval",time_hit_61,time_miss_61,0)
df_time_61_no_dummy<-build_df(df_tm20,"interval",time_hit_61,time_miss_61,1)

time_hit_21=c(16,17)
time_miss_21=c(12,13,14)
df_time_21<-build_df(df_tm20,"interval",time_hit_21,time_miss_21,0)
df_time_21_no_dummy<-build_df(df_tm20,"interval",time_hit_21,time_miss_21,1)

time_hit_1=41
time_miss_1=c(38,39)
df_time_1<-build_df(df_tm20,"interval",time_hit_1,time_miss_1,0)
df_time_1_no_dummy<-build_df(df_tm20,"interval",time_hit_1,time_miss_1,1)

# Peak position tasks initialized 
peak_hit_9=c(26,32,38)
peak_miss_9=2
df_peak_9<-build_df(df_tm20,"interval",peak_hit_9,peak_miss_9,0)
df_peak_9_no_dummy<-build_df(df_tm20,"interval",peak_hit_9,peak_miss_9,1)

peak_hit_21=41
peak_miss_21=c(17,23)
df_peak_21<-build_df(df_tm20,"interval",peak_hit_21,peak_miss_21,0)
df_peak_21_no_dummy<-build_df(df_tm20,"interval",peak_hit_21,peak_miss_21,1)

peak_hit_13=39
peak_miss_13=c(3,9)
df_peak_13<-build_df(df_tm20,"interval",peak_hit_13,peak_miss_13,0)
df_peak_13_no_dummy<-build_df(df_tm20,"interval",peak_hit_13,peak_miss_13,1)

# Model time and peak position tasks with and without metadata features 
fit_time_61<-fit_lasso(df_time_61,"interval")
fit_time_61_no_dummy<-fit_lasso(df_time_61_no_dummy,"interval")

fit_time_21<-fit_lasso(df_time_21,"interval")
fit_time_21_no_dummy<-fit_lasso(df_time_21_no_dummy,"interval")

fit_time_1<-fit_lasso(df_time_1,"interval")
fit_time_1_no_dummy<-fit_lasso(df_time_1_no_dummy,"interval")

fit_peak_9<-fit_lasso(df_peak_9,"interval")
fit_peak_9_no_dummy<-fit_lasso(df_peak_9_no_dummy,"interval")

fit_peak_21<-fit_lasso(df_peak_21,"interval")
fit_peak_21_no_dummy<-fit_lasso(df_peak_21_no_dummy,"interval")

fit_peak_13<-fit_lasso(df_peak_13,"interval")
fit_peak_13_no_dummy<-fit_lasso(df_peak_13_no_dummy,"interval")

# Writes lasso logistic regression models in a readable format
print_fit <- function(fit,name,len) {
  # No metadata features 
  if (grepl("_dum",name)){
    row_idx<-c(match("echo_genre_typ",rownames(coef(fit))),
               match("echo_artist_typ",rownames(coef(fit))),
               match("tempo",rownames(coef(fit))),
               match("energy",rownames(coef(fit))),
               match("speechiness",rownames(coef(fit))),
               match("acousticness",rownames(coef(fit))),
               match("danceability",rownames(coef(fit))),
               match("valence",rownames(coef(fit))),
               match("instrumentalness",rownames(coef(fit))),
               match("liveness",rownames(coef(fit))),
               match("key1",rownames(coef(fit))):match("key11",rownames(coef(fit))),
               match("mode1",rownames(coef(fit))),
               match("time_signature1",rownames(coef(fit))),
               match("typ",rownames(coef(fit))),
               match("genre_typ",rownames(coef(fit))),
               match("artist_typ",rownames(coef(fit))),
               match("X1",rownames(coef(fit))):match("X19",rownames(coef(fit))),
               match("(Intercept)",rownames(coef(fit)))) 
  } else{
  row_idx<-c(match("long1",rownames(coef(fit))),
                        match("success1",rownames(coef(fit))):match("success3",rownames(coef(fit))),
                        match("crossover1",rownames(coef(fit))),
                        match("reissue1",rownames(coef(fit))),
                        match("genre1",rownames(coef(fit))):match("genre12",rownames(coef(fit))),
                        match("time2",rownames(coef(fit))):match("time11",rownames(coef(fit))),
                        match("echo_genre_typ",rownames(coef(fit))),
                        match("echo_artist_typ",rownames(coef(fit))),
                        match("tempo",rownames(coef(fit))),
                        match("energy",rownames(coef(fit))),
                        match("speechiness",rownames(coef(fit))),
                        match("acousticness",rownames(coef(fit))),
                        match("danceability",rownames(coef(fit))),
                        match("valence",rownames(coef(fit))),
                        match("instrumentalness",rownames(coef(fit))),
                        match("liveness",rownames(coef(fit))),
                        match("key1",rownames(coef(fit))):match("key11",rownames(coef(fit))),
                        match("mode1",rownames(coef(fit))),
                        match("time_signature1",rownames(coef(fit))),
                        match("typ",rownames(coef(fit))),
                        match("genre_typ",rownames(coef(fit))),
                        match("artist_typ",rownames(coef(fit))),
                        match("X1",rownames(coef(fit))):match("X19",rownames(coef(fit))),
                        match("(Intercept)",rownames(coef(fit))))
  }
  
  df <-rbind(matrix(coef(fit)[row_idx,1]),len,fit$df,fit$lambda,fit$dev.ratio)
  rownames(df)<-c(rownames(coef(fit))[row_idx],"observations","df","lambda","%Dev")
  write.table(df,paste0(name,".tsv"),sep="\t",col.names=FALSE,row.names=TRUE)
}

# Print lasso logistic regression models fit to all data 
print_fit(fit_time_61,"time_61",dim(df_time_61)[1])
print_fit(fit_time_61_no_dummy,"time_61_dum",dim(df_time_61_no_dummy)[1])
print_fit(fit_time_21,"time_21",dim(df_time_21)[1])
print_fit(fit_time_21_no_dummy,"time_21_dum",dim(df_time_21_no_dummy)[1])
print_fit(fit_time_1,"time_1",dim(df_time_1)[1])
print_fit(fit_time_1_no_dummy,"time_1_dum",dim(df_time_1_no_dummy)[1])

print_fit(fit_peak_13,"peak_13",dim(df_peak_13)[1])
print_fit(fit_peak_13_no_dummy,"peak_13_dum",dim(df_peak_13_no_dummy)[1])
print_fit(fit_peak_21,"peak_21",dim(df_peak_21)[1])
print_fit(fit_peak_21_no_dummy,"peak_21_dum",dim(df_peak_21_no_dummy)[1])
print_fit(fit_peak_9,"peak_9",dim(df_peak_9)[1])
print_fit(fit_peak_9_no_dummy,"peak_9_dum",dim(df_peak_9_no_dummy)[1])

# Perform cross-validation on each model 
find_pred<-function(df,target_var,dummy,lambda){
  folds<-createFolds(df[target_var][,1], k = 10, list = TRUE, returnTrain = FALSE)
  cv<-matrix(NA, nrow=10, ncol=4)
  index=1
  
  for (i in folds){
    train_df<-df[-c(unlist(i)),]
    test_df<-df[c(unlist(i)),]
    
    # Relevel control variables 
    if (dummy==0){
      controls<-c("reissue","crossover","time","success","long","genre","key","mode","time_signature")
    }else{
      controls<-c("key","mode","time_signature")
    }
    for (con in controls){
      if (!isTRUE(all.equal(levels(factor(train_df[con][,1])),levels(factor(test_df[con][,1]))))){
        diff_indices=setdiff(levels(factor(test_df[con][,1])),levels(factor(train_df[con][,1])))
        for (ind in diff_indices){
          test_df=test_df[!test_df[con][,1]==ind,]
        }
      }
    }
    
    # Set up model 
    model<-fit_lasso(train_df,"interval",NULL)
    test_Y=test_df[target_var][,1]
    test_X=model.matrix(~.,test_df[-c(match(target_var,colnames(test_df)))])
    test_X<-test_X[,-1]
    y_pred=predict(model,test_X,type="response")
    
    cutoffs <- seq(0.1,0.9,0.05)
    f1_scores=rep(-1,length(cutoffs))
    c_ind=1
    
    # Iterate through cutoffs to find best threshold 
    for (coff in cutoffs){
      y_pred_factor<-as.factor(as.numeric(y_pred>coff))
      y_test_factor<-as.factor(as.numeric(test_df[target_var][,1]))
      levels(y_pred_factor)<-c("0","1")
      levels(y_test_factor)<-c("0","1")
      conf_mat<-table(y_pred_factor,y_test_factor)
      acc=sum(diag(conf_mat))/sum(conf_mat)
      prec = conf_mat[2,2]/sum(conf_mat[,2])
      rec = conf_mat[2,2]/sum(conf_mat[2,])
      f1=2*prec*rec/(prec+rec)
      if (!is.nan(f1)){
        f1_scores[c_ind]=f1
      }
      c_ind=c_ind+1
    }
    
    # Find best threshold based on F1 score 
    threshold=cutoffs[which.max(f1_scores)]
    y_pred_factor<-as.factor(as.numeric(y_pred>threshold))
    y_test_factor<-as.factor(as.numeric(test_df[target_var][,1]))
    levels(y_pred_factor)<-c("0","1")
    levels(y_test_factor)<-c("0","1")
    conf_mat<-table(y_pred_factor,y_test_factor)
    acc=sum(diag(conf_mat))/sum(conf_mat)
    prec = conf_mat[2,2]/sum(conf_mat[,2])
    rec = conf_mat[2,2]/sum(conf_mat[2,])
    f1=2*prec*rec/(prec+rec)
    cv[index,]=c(acc,prec,rec,f1)
    index=index+1
  }
  return(cv)
}

# Fit models based on feature sets with and without control variables
cv_time_61<-find_pred(df_time_61,"interval",0,fit_time_61$lambda)
cv_time_61_no_dummy<-find_pred(df_time_61_no_dummy,"interval",1,fit_time_61_no_dummy$lambda)
cv_time_21<-find_pred(df_time_21,"interval",0,fit_time_21$lambda)
cv_time_21_no_dummy<-find_pred(df_time_21_no_dummy,"interval",1,fit_time_21_no_dummy$lambda)
cv_time_1<-find_pred(df_time_1,"interval",0,fit_time_1$lambda)
cv_time_1_no_dummy<-find_pred(df_time_1_no_dummy,"interval",1,fit_time_1_no_dummy$lambda)

cv_peak_13<-find_pred(df_peak_13,"interval",0,fit_peak_13$lambda)
cv_peak_13_no_dummy<-find_pred(df_peak_13_no_dummy,"interval",1,fit_peak_13_no_dummy$lambda)
cv_peak_21<-find_pred(df_peak_21,"interval",0,fit_peak_21$lambda)
cv_peak_21_no_dummy<-find_pred(df_peak_21_no_dummy,"interval",1,fit_peak_21_no_dummy$lambda)
cv_peak_9<-find_pred(df_peak_9,"interval",0,fit_peak_9$lambda)
cv_peak_9_no_dummy<-find_pred(df_peak_9_no_dummy,"interval",1,fit_peak_9_no_dummy$lambda)

# Write cross-validation results to file
cv_time<-rbind(apply(cv_time_61,2,mean),apply(cv_time_61_no_dummy,2,mean),
               apply(cv_time_21,2,mean),apply(cv_time_21_no_dummy,2,mean),
               apply(cv_time_1,2,mean),apply(cv_time_1_no_dummy,2,mean))

cv_peak<-rbind(apply(cv_peak_13,2,mean),apply(cv_peak_13_no_dummy,2,mean),
               apply(cv_peak_21,2,mean),apply(cv_peak_21_no_dummy,2,mean),
               apply(cv_peak_9,2,mean),apply(cv_peak_9_no_dummy,2,mean))

rownames(cv_time)=c("time_61","time_61_no_dummy","time_21","time_21_no_dummy","time_1","time_1_no_dummy")
colnames(cv_time)=c("accuracy","precision","recall","F1")
rownames(cv_peak)=c("peak_13","peak_13_no_dummy","peak_21","peak_21_no_dummy","peak_9","peak_9_no_dummy")
colnames(cv_peak)=c("accuracy","precision","recall","F1")

write.table(cv_time,"10fold_cv_binary_time.tsv",sep="\t",col.names=TRUE,row.names=TRUE)
write.table(cv_peak,"10fold_cv_binary_peak.tsv",sep="\t",col.names=TRUE,row.names=TRUE)


