import heapq
import random
from collections import deque
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, silhouette_score

FEATURES = ["return_5d", "return_20d", "volatility_20d", "sma20_gap", "sma50_gap"]

def market_features(history):
    close = history["Close"].astype(float)
    daily = close.pct_change()
    frame = pd.DataFrame({
        "return_5d": close.pct_change(5),
        "return_20d": close.pct_change(20),
        "volatility_20d": daily.rolling(20).std(),
        "sma20_gap": close / close.rolling(20).mean() - 1,
        "sma50_gap": close / close.rolling(50).mean() - 1,
    })
    return frame.replace([np.inf, -np.inf], np.nan).dropna()

def decision_tree_analysis(history):
    f = market_features(history)
    close = history["Close"].astype(float)
    future = close.shift(-20) / close - 1
    target = future.reindex(f.index)
    mask = target.notna()
    X = f.loc[mask]
    y = pd.Series(
        np.where(target.loc[mask] > 0.02, "Positive",
                 np.where(target.loc[mask] < -0.02, "Negative", "Neutral")),
        index=X.index,
    )
    if len(X) < 120 or y.nunique() < 2:
        return None

    split = int(len(X) * 0.8)
    model = DecisionTreeClassifier(
        max_depth=5, min_samples_leaf=10, criterion="entropy", random_state=42
    )
    model.fit(X.iloc[:split], y.iloc[:split])
    test_pred = model.predict(X.iloc[split:])
    current = X.iloc[[-1]]
    prediction = model.predict(current)[0]
    probabilities = model.predict_proba(current)[0]
    confidence = float(probabilities.max())

    importance = pd.DataFrame({
        "Feature": X.columns,
        "Importance": model.feature_importances_,
    }).sort_values("Importance", ascending=False)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "accuracy": float(accuracy_score(y.iloc[split:], test_pred)),
        "depth": model.get_depth(),
        "samples": len(X),
        "importance": importance,
        "features": current.iloc[0].to_dict(),
    }

def kmeans_analysis(history, k=3):
    f = market_features(history)
    if len(f) < 80:
        return None
    cols = ["return_5d", "return_20d", "volatility_20d", "sma20_gap"]
    scaler = StandardScaler()
    z = scaler.fit_transform(f[cols])
    model = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = model.fit_predict(z)
    score = silhouette_score(z, labels)
    means = f.assign(cluster=labels).groupby("cluster")[cols].mean()
    vol_mid = means["volatility_20d"].median()
    names = {}
    for cluster, row in means.iterrows():
        if row["return_20d"] > 0.03 and row["volatility_20d"] <= vol_mid:
            names[int(cluster)] = "Growth / Low Volatility"
        elif row["volatility_20d"] > vol_mid:
            names[int(cluster)] = "High Volatility"
        elif row["return_20d"] < -0.03:
            names[int(cluster)] = "Weak / Downtrend"
        else:
            names[int(cluster)] = "Stable / Mixed"
    return {
        "cluster": int(labels[-1]),
        "regime": names[int(labels[-1])],
        "silhouette": float(score),
        "labels": labels,
        "data": f[cols].reset_index(drop=True),
    }

GRAPH = {
    "Company": [("Market Data", 1), ("Earnings Call", 1)],
    "Market Data": [("Price Trend", 1), ("Financial Health", 2)],
    "Price Trend": [("Momentum", 1)],
    "Financial Health": [("Profitability", 1)],
    "Earnings Call": [("FinBERT Sentiment", 1)],
    "Momentum": [("Decision Tree", 1)],
    "FinBERT Sentiment": [("Expert System", 1)],
    "Decision Tree": [("Expert System", 1)],
    "Profitability": [("Expert System", 2)],
    "Expert System": [("Market Regime", 1)],
    "Market Regime": [],
}
HEURISTIC = {
    "Company": 6, "Market Data": 5, "Earnings Call": 4, "Price Trend": 4,
    "Financial Health": 3, "Momentum": 3, "FinBERT Sentiment": 2,
    "Decision Tree": 1, "Profitability": 2, "Expert System": 1, "Market Regime": 0,
}

def bfs(start, goal):
    q = deque([(start, [start])])
    seen = {start}
    while q:
        node, path = q.popleft()
        if node == goal:
            return path
        for nxt, _ in GRAPH[node]:
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, path + [nxt]))
    return []

def dfs(start, goal):
    stack = [(start, [start])]
    seen = set()
    while stack:
        node, path = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        if node == goal:
            return path
        for nxt, _ in reversed(GRAPH[node]):
            stack.append((nxt, path + [nxt]))
    return []

def ucs(start, goal):
    heap = [(0, start, [start])]
    best = {start: 0}
    while heap:
        cost, node, path = heapq.heappop(heap)
        if node == goal:
            return path, cost
        for nxt, weight in GRAPH[node]:
            new_cost = cost + weight
            if new_cost < best.get(nxt, float("inf")):
                best[nxt] = new_cost
                heapq.heappush(heap, (new_cost, nxt, path + [nxt]))
    return [], None

def greedy(start, goal):
    heap = [(HEURISTIC[start], start, [start])]
    seen = set()
    while heap:
        _, node, path = heapq.heappop(heap)
        if node in seen:
            continue
        seen.add(node)
        if node == goal:
            return path
        for nxt, _ in GRAPH[node]:
            heapq.heappush(heap, (HEURISTIC[nxt], nxt, path + [nxt]))
    return []

def astar(start, goal):
    heap = [(HEURISTIC[start], 0, start, [start])]
    best = {start: 0}
    while heap:
        _, cost, node, path = heapq.heappop(heap)
        if node == goal:
            return path, cost
        for nxt, weight in GRAPH[node]:
            new_cost = cost + weight
            if new_cost < best.get(nxt, float("inf")):
                best[nxt] = new_cost
                heapq.heappush(heap, (new_cost + HEURISTIC[nxt], new_cost, nxt, path + [nxt]))
    return [], None

def weighted_score(f, weights):
    return (
        weights[0] * f["return_5d"] +
        weights[1] * f["return_20d"] +
        weights[2] * f["sma50_gap"] -
        weights[3] * f["volatility_20d"]
    )

def evaluate_weights(f, weights):
    close_proxy = f["return_20d"]
    score = weighted_score(f, weights)
    return float((np.sign(score) == np.sign(close_proxy)).mean())

def genetic_optimize_weights(f):
    population = []
    for _ in range(30):
        w = np.random.default_rng(_).random(4)
        w = w / w.sum()
        population.append(w)
    for _ in range(35):
        population.sort(key=lambda w: evaluate_weights(f, w), reverse=True)
        parents = population[:8]
        children = parents[:2]
        while len(children) < 30:
            a, b = random.sample(parents, 2)
            child = (a + b) / 2
            child += np.random.normal(0, 0.04, 4)
            child = np.clip(child, 0.001, None)
            child = child / child.sum()
            children.append(child)
        population = children
    best = max(population, key=lambda w: evaluate_weights(f, w))
    return {"weights": best, "score": evaluate_weights(f, best)}

def hill_climb_threshold(f, weights):
    best_t = 0.01
    best_score = -1
    for t in np.arange(0.01, 0.101, 0.005):
        score = weighted_score(f, weights)
        pred = np.where(score > t, 1, np.where(score < -t, -1, 0))
        actual = np.where(f["return_20d"] > 0.02, 1, np.where(f["return_20d"] < -0.02, -1, 0))
        acc = float((pred == actual).mean())
        if acc > best_score:
            best_score, best_t = acc, float(t)
    return {"threshold": best_t, "accuracy": best_score}

def forward_chain(facts, rules):
    facts = set(facts)
    changed = True
    while changed:
        changed = False
        for conditions, conclusion in rules:
            if set(conditions).issubset(facts) and conclusion not in facts:
                facts.add(conclusion)
                changed = True
    return facts

def backward_chain(goal, facts, rules):
    facts = set(facts)
    def prove(g, trail):
        if g in facts:
            return True
        if g in trail:
            return False
        return any(prove(c, trail | {g}) for conditions, conclusion in rules if conclusion == g for c in conditions)
    return prove(goal, set())

def expert_system(sentiment, tree, regime, momentum, volatility):
    facts = {"market_data_available"}
    facts.add("positive_sentiment" if sentiment > 0.15 else "negative_sentiment" if sentiment < -0.15 else "neutral_sentiment")
    facts.add("positive_momentum" if momentum > 0.03 else "negative_momentum" if momentum < -0.03 else "neutral_momentum")
    if tree:
        facts.add("tree_positive" if tree["prediction"] == "Positive" else "tree_negative" if tree["prediction"] == "Negative" else "tree_neutral")
    if "Growth" in regime:
        facts.add("growth_regime")
    elif "High Volatility" in regime:
        facts.add("high_volatility_regime")
    else:
        facts.add("stable_regime")
    if volatility < 0.025:
        facts.add("low_volatility")

    rules = [
        (["positive_sentiment", "positive_momentum"], "supportive_evidence"),
        (["negative_sentiment", "negative_momentum"], "caution_evidence"),
        (["tree_positive", "supportive_evidence"], "model_supports_positive"),
        (["tree_negative", "caution_evidence"], "model_supports_caution"),
        (["growth_regime", "low_volatility"], "favorable_regime"),
        (["supportive_evidence", "favorable_regime"], "positive_analysis_state"),
        (["caution_evidence", "high_volatility_regime"], "negative_analysis_state"),
    ]
    derived = forward_chain(facts, rules)
    if "positive_analysis_state" in derived:
        state = "Positive analysis state"
    elif "negative_analysis_state" in derived:
        state = "Caution analysis state"
    elif "supportive_evidence" in derived or "caution_evidence" in derived:
        state = "Mixed evidence"
    else:
        state = "Insufficient / neutral evidence"
    return {
        "facts": sorted(facts),
        "derived": sorted(derived),
        "rules": rules,
        "state": state,
        "backward_positive": backward_chain("positive_analysis_state", facts, rules),
    }

def csp_validate(tree, kmeans, sentiment):
    checks = {
        "historical_data_available": tree is not None and kmeans is not None,
        "sentiment_available": sentiment is not None,
        "model_output_available": tree is not None,
        "regime_output_available": kmeans is not None,
    }
    return {"checks": checks, "valid": all(checks.values())}

def run_ai_pipeline(history, sentiment_score=0.0):
    tree = decision_tree_analysis(history)
    clusters = kmeans_analysis(history)
    f = market_features(history)
    momentum = float(f["return_20d"].iloc[-1])
    volatility = float(f["volatility_20d"].iloc[-1])
    regime = clusters["regime"] if clusters else "Unknown"
    expert = expert_system(sentiment_score, tree, regime, momentum, volatility)
    ga = genetic_optimize_weights(f) if len(f) >= 80 else None
    hill = hill_climb_threshold(f, ga["weights"]) if ga else None
    return {
        "decision_tree": tree,
        "kmeans": clusters,
        "expert": expert,
        "csp": csp_validate(tree, clusters, sentiment_score),
        "optimization": {"genetic": ga, "hill_climbing": hill},
        "search": {
            "BFS": bfs("Company", "Market Regime"),
            "DFS": dfs("Company", "Market Regime"),
            "UCS": ucs("Company", "Market Regime"),
            "Greedy Best First": greedy("Company", "Market Regime"),
            "A*": astar("Company", "Market Regime"),
        },
        "features": {
            "20D momentum": momentum,
            "20D volatility": volatility,
        },
    }
