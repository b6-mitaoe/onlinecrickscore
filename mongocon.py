from flask import Flask,redirect, url_for, request,render_template,jsonify
from flask_pymongo import PyMongo
from pycricbuzz import Cricbuzz
from pprint import pprint
import json
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/cricketlive"
mongo = PyMongo(app)


@app.route("/index")
def home_page():
    
    c=Cricbuzz()


    all_matches = c.matches()
    
    
    for match in all_matches:
        
        
        if match['mchstate']=='inprogress'or match['mchstate']=='innings break':
            mongo.db.inprogress.insert(match)     
            mongo.db.inprogressmatchid.insert({"matchid":match['id']}) 
            c.livescore(match['id'])['id']=match['id']    
            mongo.db.inprogressscore.insert(c.livescore(match['id']))
            mongo.db.inprogressscorecard.insert(c.scorecard(match['id']))
            
        
                        
                    
    return render_template("index.html")   
                                      
        
        
	   
@app.route("/users")
def users():
    c=Cricbuzz()
    all_matches = c.matches()
    for match in all_matches:
        
        if match['mchstate']=='inprogress' or match['mchstate']=='innings break':
            data=mongo.db.inprogress.insert(match)  
    
    return render_template('result.html', result = mongo.db.inprogress.find())
    

    
@app.route('/completed')
def complete():
    c=Cricbuzz()
    all_matches = c.matches()
    for match in all_matches:
        
        if match['mchstate']=='complete' or match['mchstate']=='mom':
            
            if  mongo.db.completed.find().count()>0:
                mongo.db.completed.delete_one({'id':match['id']})
                result=mongo.db.completed.insert(match)
            
     
                
            else:
                result=mongo.db.completed.insert(match)
            
     
    return render_template("pastresult.html",result=mongo.db.completed.find())
            

    #return render_template('result.html', result = mongo.db.users.find({"mchstate":"preview"}))
    

    
@app.route('/preview')
def preview():
    c=Cricbuzz()
    all_matches = c.matches()
    for match in all_matches:
        if match['mchstate']=='preview':
            if  mongo.db.preview.find().count()>0:
                mongo.db.preview.delete_one({'id':match['id']})
                result=mongo.db.preview.insert(match)

            else:
                result=mongo.db.preview.insert(match)
            
     
    return render_template("previewresult.html",result=mongo.db.preview.find())
            
@app.route('/scorecard',methods=['POST'])
def checkbut():
    matid=request.form['matchid']
    
    
    c=Cricbuzz()
    all_matches = c.matches()
    
    
    for match in all_matches:
        
        if match['mchstate']=='inprogress'or match['mchstate']=='innings break' or match['mchstate']=='mom'or match['mchstate']=='complete':
            

                result=mongo.db.live.insert(c.livescore(matid))
            
                
                return render_template("score.html",result=mongo.db.live.find({"_id":result}))
        
@app.route('/predictions',methods=['POST'])
def predict():
    matid=request.form['matchid']
    team1name=request.form['team1']
    team2name=request.form['team2']
    #return render_template('result.html', result = mongo.db.users.find({"mchstate":"preview"}))
    return render_template("makeprediction.html",result=mongo.db.preview.find(),matchid=matid,team1=team1name,team2=team2name)




@app.route('/predictionsave',methods=['POST'])
def predictions():
    name=request.form['name']
    teamtowin=request.form['teamtowin']
    matchid=request.form['matchid']
    mongo.db.userpredictions.insert({'name':name,'matchid':matchid,"winner":teamtowin})
    return render_template("finalpredict.html",name=name,teamtowin=teamtowin,matchid=matchid)


@app.route('/predictionresult',methods=['POST'])
def predictionresultshow():
    result=mongo.db.userpredictions.find()
    commat=mongo.db.completed
    for i in result:
        for key,val in i.items():
            if key=='matchid':
                if commat.find({'id':val}).count()>0:
                    winteam=commat.find({'id':val},{'status':1,'_id':0})
                    winner=commat.find({"winner":{"$ne":""}},{'_id':0,'winner':1})
                    username=commat.find({"name":{"$ne":""}},{'_id':0,'name':1})
                    if commat.find({'status':{"$regex":winner}}).count()>0:
                        mongo.db.results.insert({'winner':winteam,'username':username})
            

    return render_template("winnerusers.html",result=mongo.db.results.find())                

if __name__ == '__main__':
    
    app.run(debug = True)
    

   
   