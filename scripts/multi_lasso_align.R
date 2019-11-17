# Perform multi-class lasso regression (one-against-all modeling)

rm(list = ls())

library(usdm)
library(stargazer)
library(glmnet)
library(caret)
library(ggplot2)
library(scales)


set.seed(1)

# Control variables 
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

# Build DataFrame for modeling task 
build_df <- function(df,target_var,categories,dummy){
  df<-unique(df)
  
  # Exclude metadata features 
  if (dummy==1){
    df<-df[-c(match("reissue",colnames(df)),match("success",colnames(df)),match("genre",colnames(df)),match("crossover",colnames(df)),match("time",colnames(df)),match("long",colnames(df)))]
    v<-vifstep(df[-c(match("interval",colnames(df)),match("align",colnames(df)),match("X0",colnames(df)))],4)
    df$key<-as.factor(df$key)
    df$mode<-as.factor(df$mode)
    df$time_signature<-as.factor(df$time_signature)
  }
  else{
    v<-vifstep(df[-c(match("interval",colnames(df)),match("align",colnames(df)),match("X0",colnames(df)))],4)
    df<-control_df(df,FALSE)
  }
  df_colnames<-colnames(exclude(df,v))
  df<-df[c(df_colnames,target_var)]
  
  # Relevel classes 
  mega_agr_hit<-as.logical((df[target_var][,1]==-1))
  for (i in  seq(length(categories))){
    agr_hit=as.logical((df[target_var][,1]==-1))
    for (h in unlist(categories[i])){
      agr_hit=as.logical(agr_hit+as.logical((df[target_var][,1]==h)))
    }
    df[as.logical(agr_hit),][target_var][,1]=-i-1
    mega_agr_hit<-mega_agr_hit+agr_hit
  }
  df<-df[as.logical((mega_agr_hit)),]
  df[target_var][,1]<-df[target_var]*-1
  df[target_var][,1]<-as.factor(df[target_var][,1]-1)
  return(df)
}

# Fit multi-class lasso logistic regression 
fit_lasso <- function(df,target_var,lambda=NULL) {
  Y=df[target_var][,1]
  X=model.matrix(~.,df[-c(match(target_var,colnames(df)))])
  X<-X[,-1]
  
  if(!is.null(lambda)){
    penalty_fit <-glmnet(x = X, y = Y, alpha = 1, lambda = lambda,family="multinomial")
    return(penalty_fit)
  }
  
  crossval <-  cv.glmnet(x = X, y = Y,alpha=1,family="multinomial",nfolds=10,type.multinomial = "grouped")
  penalty <- crossval$lambda.1se 
  penalty_fit <-glmnet(x = X, y = Y,alpha=1,lambda=penalty,family="multinomial") 
  return(penalty_fit)
}

# Fit binary lasso logistic regression 
fit_lasso2 <- function(df,target_var,lambda=NULL) {
  Y=df[target_var][,1]
  X=model.matrix(~.,df[-c(match(target_var,colnames(df)))])
  X<-X[,-1]
  
  if(!is.null(lambda)){
    penalty_fit <-glmnet(x = X, y = Y, alpha = 1, lambda = lambda,family="binomial")
    return(penalty_fit)
  }
  
  crossval <-  cv.glmnet(x = X, y = Y,alpha=1,family="binomial",nfolds=10)
  penalty <- crossval$lambda.1se 
  penalty_fit <-glmnet(x = X, y = Y, alpha = 1, lambda = penalty,family="binomial")
  return(penalty_fit)
}

# Perform cross-validation on model
find_pred<-function(df,target_var,dummy,lambda){
  folds<-createFolds(df[target_var][,1], k = 10, list = TRUE, returnTrain = FALSE)
  cv<-matrix(NA, nrow=10, ncol=4)
  index=1
  # Confusion matrix needed to store classification results for each individual model 
  mega_conf_mat<-matrix(0, nrow=length(levels(df[target_var][,1])), ncol=length(levels(df[target_var][,1])))
  
  # Relevel control variables 
  for (i in folds){
    train_df<-df[-c(unlist(i)),]
    test_df<-df[c(unlist(i)),]
    
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
    
    # Fit model over training data 
    model<-fit_lasso(train_df,"align",NULL)
    
    train_Y=train_df[target_var][,1]
    train_X=model.matrix(~.,train_df[-c(match(target_var,colnames(train_df)))])
    train_X<-train_X[,-1]
    
    test_Y=test_df[target_var][,1]
    test_X=model.matrix(~.,test_df[-c(match(target_var,colnames(test_df)))])
    test_X<-test_X[,-1]
    
    # Predict test labels 
    y_pred=predict(model,test_X,type="class")
    y_pred_factor<-factor(y_pred,levels=seq(length(levels(df[target_var][,1]))))
    y_test_factor<-factor(test_df[target_var][,1],levels=seq(length(levels(df[target_var][,1]))))
    conf_mat<-table(y_pred_factor,y_test_factor)
    mega_conf_mat<-mega_conf_mat+conf_mat
    
    acc=sum(diag(conf_mat))/sum(conf_mat)
    prec=matrix(0, nrow=length(levels(y_pred_factor)), ncol=1)
    rec=matrix(0, nrow=length(levels(y_pred_factor)), ncol=1)
    f1=matrix(0, nrow=length(levels(y_pred_factor)), ncol=1)
    
    for (j in seq(length(levels(y_pred_factor)))){
      prec[j] = (conf_mat[j,j]+0.0000000000001)/(sum(conf_mat[,j])+0.00001)
      rec[j] = (conf_mat[j,j]+0.0000000000001)/(sum(conf_mat[j,])+0.00001)
      f1[j]=2*prec[j]*rec[j]/(prec[j]+rec[j])
    }
    cv[index,]=c(acc,mean(prec),mean(rec),mean(f1))
    index=index+1
  }
  return(mega_conf_mat)
}

# Read in data and format as DataFrames with and without metadata features 
path_tm20="thesis/data/model0_data.tsv"
df_tm20=read.table(file=path_tm20,sep='\t',header=TRUE)
classes<-list(c(7),c(28),c(2),c(10),c(34))
dfs<-build_df(df_tm20,"align",classes,0)

# Downsample classes, so each class is equal
down_df<-downSample(x = dfs[, -ncol(dfs)],y = dfs$align)
colnames(down_df)<-colnames(dfs)
dfs_no_dummy<-build_df(df_tm20,"align",classes,1)
down_df_dummy<-downSample(x = dfs_no_dummy[, -ncol(dfs_no_dummy)],y = dfs_no_dummy$align)
colnames(down_df_dummy)<-colnames(dfs_no_dummy)

# Fit lasso regression models
df_fit<-fit_lasso(down_df,"align")
df_fit_no_dummy<-fit_lasso(down_df_dummy,"align")

# Perform cross-validation
cv_conf_mat<-find_pred(down_df,"align",0,df_fit$lambda)
cv_conf_mat_no_dummy<-find_pred(down_df_dummy,"align",1,df_fit_no_dummy$lambda)

# Write cross-validation results t o file
write.table(cv_conf_mat,"multi_conf_mat.tsv",sep="\t",col.names=TRUE,row.names=TRUE)
write.table(cv_conf_mat_no_dummy,"multi_conf_mat_no_dummy.tsv",sep="\t",col.names=TRUE,row.names=TRUE)

# Build visual confusion matrices 
rownames(cv_conf_mat)<-c("A","B","C","D","E")
colnames(cv_conf_mat)<-c("A","B","C","D","E")
rownames(cv_conf_mat_no_dummy)<-c("A","B","C","D","E")
colnames(cv_conf_mat_no_dummy)<-c("A","B","C","D","E")
caret_cv_conf_mat<-confusionMatrix(cv_conf_mat)
caret_cv_conf_mat_no_dummy<-confusionMatrix(cv_conf_mat_no_dummy)

# Confusion matrix plotting 
ggplotConfusionMatrix <- function(m){
  mytitle <- paste("Accuracy", percent_format()(m$overall[1]),
                   "Kappa", percent_format()(m$overall[2]))
  p <-
    ggplot(data = as.data.frame(m$table) ,
           aes(x = y_test_factor, y = y_pred_factor)) +
    geom_tile(aes(fill = log(Freq+1)), colour = "firebrick3") +
    scale_fill_gradient(low = "white", high = "firebrick3") +
    geom_text(aes(x = y_test_factor, y = y_pred_factor, label = Freq)) +
    theme(legend.position = "none") +
    ggtitle(mytitle) +
    xlab("Ground truth label")  +
    ylab("Predicted label")
  return(p)
}

ggplotConfusionMatrix(caret_cv_conf_mat)
ggplotConfusionMatrix(caret_cv_conf_mat_no_dummy)

# Print lasso logistic regression models 
print_fit <- function(fit,name,len) {
  # Iterate through each one-against-all model and get its coefficients 
  for (i in seq(length(coef(fit)))){
    if (i==1){
      coef_fit=coef(fit)$`1`
    } else if(i==2){
      coef_fit=coef(fit)$`2`
    } else if(i==3){
      coef_fit=coef(fit)$`3`
    } else if(i==4){
      coef_fit=coef(fit)$`4`
    } else if(i==5){
      coef_fit=coef(fit)$`5`
    }

  # No metadata features included
  if (grepl("_dum",name)){
    row_idx<-c(match("echo_genre_typ",rownames(coef_fit)),
               match("tempo",rownames(coef_fit)),
               match("energy",rownames(coef_fit)),
               match("speechiness",rownames(coef_fit)),
               match("acousticness",rownames(coef_fit)),
               match("danceability",rownames(coef_fit)),
               match("valence",rownames(coef_fit)),
               match("instrumentalness",rownames(coef_fit)),
               match("liveness",rownames(coef_fit)),
               match("key1",rownames(coef_fit)):match("key11",rownames(coef_fit)),
               match("mode1",rownames(coef_fit)),
               match("time_signature1",rownames(coef_fit)),
               match("typ",rownames(coef_fit)),
               match("genre_typ",rownames(coef_fit)),
               match("artist_typ",rownames(coef_fit)),
               match("X1",rownames(coef_fit)):match("X9",rownames(coef_fit)),
               match("",rownames(coef_fit))) 
  }else{

    row_idx<-c(match("long1",rownames(coef_fit)),
               match("success1",rownames(coef_fit)):match("success3",rownames(coef_fit)),
               match("crossover1",rownames(coef_fit)),
               match("reissue1",rownames(coef_fit)),
               match("genre1",rownames(coef_fit)):match("genre12",rownames(coef_fit)),
               match("time2",rownames(coef_fit)):match("time11",rownames(coef_fit)),
               match("echo_genre_typ",rownames(coef_fit)),
               match("tempo",rownames(coef_fit)),
               match("energy",rownames(coef_fit)),
               match("speechiness",rownames(coef_fit)),
               match("acousticness",rownames(coef_fit)),
               match("danceability",rownames(coef_fit)),
               match("valence",rownames(coef_fit)),
               match("instrumentalness",rownames(coef_fit)),
               match("liveness",rownames(coef_fit)),
               match("key1",rownames(coef_fit)):match("key11",rownames(coef_fit)),
               match("mode1",rownames(coef_fit)),
               match("time_signature1",rownames(coef_fit)),
               match("typ",rownames(coef_fit)),
               match("genre_typ",rownames(coef_fit)),
               match("artist_typ",rownames(coef_fit)),
               match("X1",rownames(coef_fit)):match("X9",rownames(coef_fit)),
               match("",rownames(coef_fit)))
    
  }
  
  df <-rbind(matrix(coef_fit[row_idx,1]),len,fit$df,fit$lambda,fit$dev.ratio)
  rownames(df)<-c(rownames(coef_fit)[row_idx],"observations","df","lambda","%Dev")
  write.table(df,paste0(name,i,".tsv"),sep="\t",col.names=FALSE,row.names=TRUE)
  }
}

# Write lasso logistic regression results to file
print_fit(df_fit,"multiclass_lasso",dim(down_df)[1])
print_fit(df_fit_no_dummy,"multiclass_lasso_dum",dim(down_df_dummy)[1])

