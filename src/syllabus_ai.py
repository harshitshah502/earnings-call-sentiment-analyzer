import heapq
import random
from collections import deque
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, silhouette_score

def market_features(history):
    h = history.copy()
    close = h["Close"].astype(float)
    ret5 = close.pct_change(5)
    ret20 = close.pct_change(20)
    vol20 = close.pct_change().rolling(20).std()
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    momentum = close / sma20 - 1
    rows = pd.DataFrame({
        "return_5d": ret5,
        "return_20d": ret20,
        "volatility_20d": vol20,
        "sma20_gap": momentum,
        "sma50_gap": close / sma50 - 1,
    }).dropna()
    return rows

def decision_tree_analysis(history):
    f = market_features(history)
    if len(f) < 80:
        return None
    future = history["Close"].astype(float).shift(-20) / history["Close"].astype(float) - 1
    y = pd.Series(np.where(future.reindex(f.index) > 0.02, "Positive",
                  np.where(future.reindex(f.index) < -0.02, "Negative", "Neutral")),
                  index=f.index)
    valid = y.notna()
    X, y = f.loc[valid], y.loc[valid]
    if len(X) < 60 or y.nunique() < 2:
        return None
    split = int(len(X) * 0.8)
    model = DecisionTreeClassifier(max_depth=4, min_samples_leaf=8, criterion="entropy", random_state=42)
    model.fit(X.iloc[:split], y.iloc[:split])
    pred_test = model.predict(X.iloc[split:])
    acc = accuracy_score(y.iloc[split:], pred_test)
    current = X.iloc[[-1]]
    prediction = model.predict(current)[0]
    probs = model.predict_proba(current)[0]
    confidence = float(max(probs))
    importance = pd.DataFrame({"Feature": X.columns, "Importance": model.feature_importances_}).sort_values("Importance", ascending=False)
    return {"prediction": prediction, "confidence": confidence, "accuracy": float(acc), "depth": model.get_depth(), "importance": importance}

def kmeans_analysis(history, k=3):
    f = market_features(history)
    if len(f) < 40:
        return None
    X = f[["return_5d","return_20d","volatility_20d","sma20_gap"]].copy()
    scaler = StandardScaler()
    z = scaler.fit_transform(X)
    model = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = model.fit_predict(z)
    score = silhouette_score(z, labels) if len(set(labels)) > 1 else 0
    current_cluster = int(labels[-1])
    means = X.assign(cluster=labels).groupby("cluster").mean()
    labels_named = {}
    for cluster, row in means.iterrows():
        if row["return_20d"] > 0.03 and row["volatility_20d"] < means["volatility_20d"].median():
            labels_named[int(cluster)] = "Growth Regime"
        elif row["volatility_20d"] > means["volatility_20d"].median():
            labels_named[int(cluster)] = "High Volatility"
        else:
            labels_named[int(cluster)] = "Mixed / Stable"
    return {"cluster": current_cluster, "regime": labels_named[current_cluster], "silhouette": float(score), "labels": labels, "data": X.reset_index(drop=True)}

GRAPH = {
    "Market Snapshot": [("Price Trend",1),("Financial Health",2),("Earnings Sentiment",2)],
    "Price Trend": [("Momentum",1)],
    "Financial Health": [("Revenue",1),("Profitability",1)],
    "Earnings Sentiment": [("Management Tone",1)],
    "Momentum": [("Market Regime",2)],
    "Revenue": [("Market Regime",3)],
    "Profitability": [("Market Regime",2)],
    "Management Tone": [("Market Regime",2)],
    "Market Regime": []
}
HEURISTIC = {"Market Snapshot":4,"Price Trend":3,"Financial Health":3,"Earnings Sentiment":2,"Momentum":2,"Revenue":2,"Profitability":1,"Management Tone":1,"Market Regime":0}

def bfs(start, goal):
    q=deque([(start,[start])]); seen={start}
    while q:
        node,path=q.popleft()
        if node==goal:return path
        for nxt,_ in GRAPH[node]:
            if nxt not in seen: seen.add(nxt); q.append((nxt,path+[nxt]))
    return []

def dfs(start, goal):
    stack=[(start,[start])]; seen=set()
    while stack:
        node,path=stack.pop()
        if node in seen: continue
        seen.add(node)
        if node==goal:return path
        for nxt,_ in reversed(GRAPH[node]): stack.append((nxt,path+[nxt]))
    return []

def ucs(start, goal):
    heap=[(0,start,[start])]; best={start:0}
    while heap:
        cost,node,path=heapq.heappop(heap)
        if node==goal:return path,cost
        for nxt,w in GRAPH[node]:
            nc=cost+w
            if nc<best.get(nxt,float("inf")):
                best[nxt]=nc; heapq.heappush(heap,(nc,nxt,path+[nxt]))
    return [],None

def greedy(start, goal):
    heap=[(HEURISTIC[start],start,[start])]; seen=set()
    while heap:
        _,node,path=heapq.heappop(heap)
        if node in seen:continue
        seen.add(node)
        if node==goal:return path
        for nxt,_ in GRAPH[node]: heapq.heappush(heap,(HEURISTIC[nxt],nxt,path+[nxt]))
    return []

def astar(start, goal):
    heap=[(HEURISTIC[start],0,start,[start])]; best={start:0}
    while heap:
        _,cost,node,path=heapq.heappop(heap)
        if node==goal:return path,cost
        for nxt,w in GRAPH[node]:
            nc=cost+w
            if nc<best.get(nxt,float("inf")):
                best[nxt]=nc; heapq.heappush(heap,(nc+HEURISTIC[nxt],nc,nxt,path+[nxt]))
    return [],None

def hill_climb():
    x=0
    for _ in range(50):
        neighbors=[x-1,x+1]
        best=max(neighbors,key=lambda n: -(n-5)**2)
        if -(best-5)**2 <= -(x-5)**2: break
        x=best
    return x

def genetic_algorithm():
    pop=[random.randint(0,31) for _ in range(20)]
    for _ in range(30):
        pop=sorted(pop,key=lambda x: -(x-27)**2, reverse=False)
        parents=pop[:6]
        children=[]
        while len(children)<14:
            a,b=random.sample(parents,2)
            mask=1<<random.randint(0,4)
            child=(a & ~mask) | (b & mask)
            if random.random()<0.15: child ^= mask
            children.append(child)
        pop=parents+children
    return max(pop,key=lambda x: -(x-27)**2)

def minimax(depth, maximizing, values):
    if depth==0:return values[0]
    vals=[minimax(depth-1,not maximizing,values) for _ in range(2)]
    return max(vals) if maximizing else min(vals)

def alpha_beta(depth, alpha, beta, maximizing, values):
    if depth==0:return values[0]
    if maximizing:
        value=-float("inf")
        for _ in range(2):
            value=max(value,alpha_beta(depth-1,alpha,beta,False,values))
            alpha=max(alpha,value)
            if alpha>=beta:break
        return value
    value=float("inf")
    for _ in range(2):
        value=min(value,alpha_beta(depth-1,alpha,beta,True,values))
        beta=min(beta,value)
        if alpha>=beta:break
    return value

def forward_chain(facts, rules):
    facts=set(facts); changed=True
    while changed:
        changed=False
        for conditions, conclusion in rules:
            if set(conditions).issubset(facts) and conclusion not in facts:
                facts.add(conclusion); changed=True
    return facts

def backward_chain(goal, facts, rules):
    facts=set(facts)
    def prove(g, trail):
        if g in facts:return True
        if g in trail:return False
        return any(prove(c,trail|{g}) for cs,c in rules if c==g for c in cs)
    return prove(goal,set())

def csp_demo():
    domains={"Technical":"High","Sentiment":"Positive","Risk":"Low"}
    constraints=[domains["Technical"]=="High",domains["Sentiment"]=="Positive",domains["Risk"]=="Low"]
    return {"assignment":domains,"consistent":all(constraints)}

def run_syllabus_suite(history, sentiment_score=0.0):
    tree=decision_tree_analysis(history)
    clusters=kmeans_analysis(history)
    facts={"market_data_available"}
    if sentiment_score>0.15:facts.add("positive_sentiment")
    elif sentiment_score<-0.15:facts.add("negative_sentiment")
    else:facts.add("neutral_sentiment")
    f=market_features(history)
    momentum=float(f["return_20d"].iloc[-1]) if len(f) else 0
    if momentum>0.03:facts.add("positive_momentum")
    elif momentum<-0.03:facts.add("negative_momentum")
    else:facts.add("neutral_momentum")
    rules=[
        (["positive_sentiment","positive_momentum"],"supportive_evidence"),
        (["negative_sentiment","negative_momentum"],"caution_evidence"),
        (["positive_sentiment","negative_momentum"],"mixed_evidence"),
        (["negative_sentiment","positive_momentum"],"mixed_evidence"),
        (["supportive_evidence"],"positive_analysis_state"),
        (["caution_evidence"],"negative_analysis_state"),
        (["mixed_evidence"],"neutral_analysis_state"),
    ]
    derived=forward_chain(facts,rules)
    return {
        "decision_tree":tree,
        "kmeans":clusters,
        "search":{
            "BFS":bfs("Market Snapshot","Market Regime"),
            "DFS":dfs("Market Snapshot","Market Regime"),
            "UCS":ucs("Market Snapshot","Market Regime"),
            "Greedy Best First":greedy("Market Snapshot","Market Regime"),
            "A*":astar("Market Snapshot","Market Regime")
        },
        "optimization":{"Hill Climbing optimum":hill_climb(),"Genetic Algorithm optimum":genetic_algorithm()},
        "adversarial":{"Minimax":minimax(3,True,[3]),"Alpha-Beta":alpha_beta(3,-float("inf"),float("inf"),True,[3])},
        "logic":{"facts":sorted(facts),"derived":sorted(derived),"forward_chaining":"completed","backward_chaining_positive_state":backward_chain("positive_analysis_state",facts,rules)},
        "csp":csp_demo()
    }
