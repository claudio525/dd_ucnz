#encn404.py
from ipywidgets import*
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.cluster import DBSCAN

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def _rolling_window(Tm, Tsd, Ti, ts):
    # read in some data
    #ts=pd.read_csv('traffic_data.csv',parse_dates=[0]).set_index('time')['density']

    # plot the raw data
    f,(ax1,ax2,ax3)=plt.subplots(1,3, figsize=(16,4))
    for ax in [ax1,ax2,ax3]:
        ts.plot(style='k-', lw=0.5, ax=ax, label='raw data')

    # Calculate a rolling mean
    #Tm=150
    ts.rolling(window=Tm).mean().plot(style='b',ax=ax1)

    # Calculate a rolling standard deviation
    #Tsd=30
    ts.rolling(window=Tsd).std().plot(style='b', ax=ax2.twinx())

    # Calculate a rolling X-day harmonic 
    def rolling_fft(x, ti):
        fft = np.fft.fft(x)/len(x)
        psd = np.abs(fft)**2/2
        period_of_interest = ti
        ts=1./(np.fft.fftfreq(len(x)))
        i=np.argmin(abs(ts-ti))
        return psd[i]

    #Ti=30   # harmonic (days)
    ts.rolling(window=240).apply(rolling_fft, args=(Ti,)).plot(style='b', ax=ax3.twinx())

    for ax in [ax1,ax2,ax3]:
        ax.set_ylabel('traffic density')
    ax1.set_title(f'feature 1: {Tm:d}-day average')
    ax2.set_title(f'feature 2: {Tsd:d}-day std. dev.')
    ax3.set_title(f'feature 3: {Ti:d}-day harmonic')
def rolling_window():    
    Tm=IntSlider(value=150, min=20, max=240, step=10, description='$T_m$', continuous_update=False)
    Tsd=IntSlider(value=30, min=20, max=120, step=10, description='$T_{sd}$', continuous_update=False)
    Ti=IntSlider(value=30, min=10, max=50, step=5, description='$T_i$', continuous_update=False)
    ts=pd.read_csv('traffic_data.csv',parse_dates=[0]).set_index('time')['density']
    io=interactive_output(_rolling_window, {'Tm':Tm,'Tsd':Tsd,'Ti':Ti,'ts':fixed(ts)})
    return VBox([HBox([Tm, Tsd, Ti]),io])

def _clustering(step):
    # Data points (3 2D coordinates)
    data_points = np.array([[1., 6.], [3., 4.], [4., 10.], [3., 10.], [2., 8.]])
    num_clusters = 2

    # Initialize centroids (randomly)
    centroids = np.array([[-1., 7.], [6., 7.]])

    # Lists to store cluster assignments and centroids at each iteration
    cluster_assignments_history = []
    centroids_history = [centroids.copy()]

    # Perform K-means for 3 iterations
    for _ in range(4):
        # Step 1: Assign data points to clusters
        distances = np.linalg.norm(data_points[:, np.newaxis] - centroids, axis=2)
        cluster_assignments = np.argmin(distances, axis=1)
        cluster_assignments_history.append(cluster_assignments.copy())

        # Step 2: Update centroids
        for i in range(num_clusters):
            centroids[i] = np.mean(data_points[cluster_assignments == i], axis=0)
            distances = np.linalg.norm(data_points[cluster_assignments == i, np.newaxis] - centroids, axis=2)**2
        centroids_history.append(centroids.copy())
    centroids_history.append(centroids.copy())

    # Plot the clusters and membership at each iteration
    f,axs=plt.subplots(1, 4, figsize=(12, 2.5))
    f.set_facecolor((1,1,1,0))
    for ax in axs:
        ax.set_xlim([-2, 7])
        ax.set_ylim([2, 11])
        ax.set_xlabel('x')
    axs[0].set_ylabel('y')
    axs[0].set_title('initialise')
    [ax.set_title(f'iteration {i+1}') for i,ax in enumerate(axs[1:])]
    axs[0].plot(data_points[:, 0], data_points[:, 1], 'bs', ms=10, label='data')
    axs[0].plot(centroids_history[0][:, 0], centroids_history[0][:, 1], 'bo', mfc='w', mew=1.5, ms=10, label='centroid')
    axs[0].legend()
    if step==0: 
        return

    cs=['r','g']
    centroids_history=np.array(centroids_history)
    th=np.linspace(0,2*np.pi,101)
    for i,ax in enumerate(axs[1:]):
        for j,c in enumerate(cs):
            inds=np.where(cluster_assignments_history[i]==j)
            xs,ys=data_points[inds,:].T
            ax.plot(xs, ys,  c+'s', ms=10)
            cx=centroids_history[i,j,0]
            cy=centroids_history[i,j,1]
            ax.plot(cx,cy, c+'o', mfc='w', mew=1.5, ms=10)
            rm=np.max(np.sqrt((xs-cx)**2+(ys-cy)**2))
            # ax.plot(rm*np.sin(th)+cx, rm*np.cos(th)+cy, c+'--', lw=0.5)
            # print(centroids_history[i+1,j,:])
            # print(np.sum((xs-cx)**2+(ys-cy)**2))  
            
        if i*2+1 == step:
            return
        
        for j,c in enumerate(cs):
            ax.plot(centroids_history[i+1,j,0], centroids_history[i+1,j,1], c+'o', ms=10, mfc='w', mew=1.5, zorder=2)
            x0,x1=centroids_history[i:i+2,j,0]
            y0,y1=centroids_history[i:i+2,j,1]
            ax.arrow(x0,y0,(x1-x0)*0.85,(y1-y0)*0.85, color=c, length_includes_head=True, head_width=0.3, head_length=0.3, zorder=5)
        if (i+1)*2 == step:          
            return
def clustering():
    step=IntSlider(value=0, min=0, max=5, step=1, description='step', continuous_update=False)
    io=interactive_output(_clustering, {'step':step})
    return VBox([step,io])

def _kmeans(step):
    # Generate three overlapping clusters of normally distributed data
    n_samples = 300
    n_features = 2
    n_clusters = 3
    random_state = 42

    X, y = make_blobs(n_samples=n_samples, n_features=n_features, centers=n_clusters, random_state=random_state)

    # Create a scatter plot of the generated data
    f,(ax1,ax2)=plt.subplots(1,2,figsize=(12, 5))
    ax2.set_title("Silhouette Score vs. Number of Clusters")
    ax2.set_xlabel("Number of Clusters")
    ax2.set_ylabel("Silhouette Score")
    ax2.set_xlim([1.9, 5.1])
    ax2.set_ylim([0.47, 0.87])
    ax2.set_xticks([2,3,4,5])
    ax2.grid()
    
    ax1.set_title(f"KMeans Clustering (raw data)")
    ax1.set_xlabel("Feature 1")
    ax1.set_ylabel("Feature 2")
    plt.tight_layout()

    if step == 0:
        ax1.scatter(X[:, 0], X[:, 1], c='gray', marker='o', edgecolor='k', s=50, label='Data points')
        ax1.legend()
        return
    
    # Run KMeans clustering for different number of clusters
    cluster_range = []
    silhouette_scores = []

    for n in [2, 3, 4, 5]:
        kmns = KMeans(n_clusters=n, random_state=random_state)
        kmns.fit(X)
        y_pred = kmns.predict(X)
        cluster_range.append(n)
        
        # Calculate silhouette score
        silhouette_scores.append(silhouette_score(X, y_pred))

        if n-1 == step:
            break

    # Create a scatter plot for each iteration
    ax1.scatter(X[:, 0], X[:, 1], c=y_pred, cmap='viridis', marker='o', edgecolor='k', s=50)
    ax1.scatter(kmns.cluster_centers_[:, 0], kmns.cluster_centers_[:, 1], c='red', marker='x', s=100, label='Cluster centers')
    ax1.set_title(f"KMeans Clustering (k={n})")
    ax1.legend()

    # Plot silhouette scores
    ax2.plot(cluster_range, silhouette_scores, marker='o')

def kmeans():
    step=IntSlider(value=0, min=0, max=4, step=1, description='step', continuous_update=False)
    io=interactive_output(_kmeans, {'step':step})
    return VBox([step,io])

from collections import Counter

def assign_running_count(input_sequence):
    counts = Counter(input_sequence)
    unique_values_with_counts = list(counts.items())

    output_sequence = []
    for value in input_sequence:
        count = counts[value]
        output_sequence.append(count)
        counts[value] -= 1

    return output_sequence

def _split_feature(fd1,fd2,fd3,check,sl1,sl2,sl3,df):
    f,(ax,ax1)=plt.subplots(1,2,figsize=(12, 4))
    ax_=ax.twinx()
    df1=df.loc[df[fd1]>sl1,:]
    df0=df.loc[df[fd1]<=sl1,:]
    ms=30
    ax.plot(df0.loc[df0["safe"],fd1], df0.loc[df0["safe"],fd2], 'go', ms=ms)
    ax.plot(df0.loc[~df0["safe"],fd1], df0.loc[~df0["safe"],fd2], 'ro', ms=ms)
    ax_.plot(df1.loc[df1["safe"],fd1], df1.loc[df1["safe"],fd3], 'go', ms=ms)
    ax_.plot(df1.loc[~df1["safe"],fd1], df1.loc[~df1["safe"],fd3], 'ro', ms=ms)
    ax.plot([],[], 'go', ms=10, label='safe')
    ax.plot([],[], 'ro', ms=10, label='unsafe')
    ax.axvline(x=sl1, color="gray", linestyle="--")#, label=f"Split at {fd1}={sl1:.1f}")
    ax.set_xlabel(fd1)
    # ax.set_yticks([])
    ax.set_ylabel(fd2)
    ax_.set_ylabel(fd3)
    if check:
        xlim=ax.get_xlim()
        ax.set_xlim(xlim)
        if fd2=="material_type":
            sl2=0.5
        if fd3=="material_type":
            sl3=0.5
        ax.plot([xlim[0], sl1], [sl2, sl2], '--', color='gray')
        ax_.plot([sl1, xlim[1]], [sl3, sl3], '--', color='gray')
    else:
        ylim0=ax.get_ylim()
        ylim1=ax_.get_ylim()
        ax.set_ylim([np.min([ylim0[0], ylim1[0]]),np.max([ylim0[-1], ylim1[-1]])])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1))

    ax1.set_xlim([-0.3, 2.5])
    ax1.set_ylim([-3.5, 3.5])
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.axis('off')
    bb=dict(facecolor='white', edgecolor='black')
    ax1.plot([0,1],[0,2], 'k-')
    ax1.plot([0,1],[0,-2], 'k-')
    if check:
        ax1.plot([1,2],[2,3], 'k-')
        ax1.plot([1,2],[2,1], 'k-')
        ax1.plot([1,2],[-2,-3], 'k-')
        ax1.plot([1,2],[-2,-1], 'k-')

    if not check:
        c2=[0.5,0.5,0.5]
        c1='k'
    else:
        c1=[0.5,0.5,0.5]
        c2='k'
    ax1.text(0, 0, f'{fd1}\n>{sl1:.1f}', ha='center', bbox=bb, color=c1)
    if check:
        if fd2 == 'material_type':
            txt=f'{fd2}\n is steel'
        else:
            txt=f'{fd2}\n>{sl2:.1f}'
        ax1.text(1, -2, txt, ha='center', bbox=bb, color=c2)
        if fd3 == 'material_type':
            txt=f'{fd3}\n is steel'
        else:
            txt=f'{fd3}\n>{sl3:.1f}'
        ax1.text(1, 2, txt, ha='center', bbox=bb, color=c2)

    if fd2 == 'material_type':
        df00=df0.loc[df0[fd2]=='Steel',:]
        df01=df0.loc[df0[fd2]=='Concrete',:]
    else:
        df00=df0.loc[df0[fd2]>sl2,:]
        df01=df0.loc[df0[fd2]<=sl2,:]
    if fd3=='material_type':
        df10=df1.loc[df1[fd3]=='Steel',:]
        df11=df1.loc[df1[fd3]!='Steel',:]
    else:
        df10=df1.loc[df1[fd3]>sl3,:]
        df11=df1.loc[df1[fd3]<=sl3,:]

    if check:
        ys=[-1,-3,3,1]
        dfs=[df00,df01,df10,df11]
    else:
        ys=[-2,2]
        dfs=[df0,df1]
    for y,dfi in zip(ys, dfs):
        if dfi.shape[0]==0:
            s=0;us=0
        else:
            s=dfi['safe'].sum()
            us=dfi.shape[0]-s
        if check:
            ax1.text(2, y, f'{s:d} Safe\n{us:d} Unsafe', bbox=bb, ha='center', color=c2)
        else:
            ax1.text(1, y, f'{s:d} Safe\n{us:d} Unsafe', bbox=bb, ha='center', color=c2)
        
    bb=dict(facecolor='white', edgecolor='blue', boxstyle='round')
    ax1.text(0.5, 1, 'True', ha='center', bbox=bb, style='italic', color='b')
    ax1.text(0.5, -1, 'False', ha='center', bbox=bb, style='italic', color='b')
    if check:
        ax1.text(1.5, 2.5, 'True', ha='center', bbox=bb, style='italic', color='b')
        ax1.text(1.5, 1.5, 'False', ha='center', bbox=bb, style='italic', color='b')
        ax1.text(1.5, -1.5, 'True', ha='center', bbox=bb, style='italic', color='b')
        ax1.text(1.5, -2.5, 'False', ha='center', bbox=bb, style='italic', color='b')

    if fd2 == fd3:
        y0=np.min([axi.get_ylim()[0] for axi in [ax,ax_]])
        y1=np.max([axi.get_ylim()[1] for axi in [ax,ax_]])
        [axi.set_ylim([y0,y1]) for axi in [ax,ax_]]

    plt.show()

def decision_tree():
    # Create the dataframe
    data = [
        {"load_capacity": 50, "material_type": "Concrete", "age": 10, "safe": False},
        {"load_capacity": 30, "material_type": "Concrete", "age": 5, "safe": True},
        {"load_capacity": 70, "material_type": "Concrete", "age": 25, "safe": False},
        {"load_capacity": 70, "material_type": "Steel", "age": 35, "safe": False},
        {"load_capacity": 60, "material_type": "Steel", "age": 15, "safe": True},
        {"load_capacity": 50, "material_type": "Steel", "age": 8, "safe": True},
        {"load_capacity": 35, "material_type": "Steel", "age": 3, "safe": True}
    ]
    df = pd.DataFrame(data)

    
    # Create the interactive widgets
    fd1 = widgets.Dropdown(value='load_capacity', options=["load_capacity", "age"], description="Feature:")
    fd2 = widgets.Dropdown(value='age', options=["load_capacity", "age", "material_type"], description="Feature:")
    fd3 = widgets.Dropdown(value='age', options=["load_capacity", "age", "material_type"], description="Feature:")
    check = Checkbox(value=False, description="lock root node")

    sl1 = widgets.FloatSlider(
        value=50,
        min=min(df["load_capacity"].min(), df["age"].min())-1,
        max=max(df["load_capacity"].max(), df["age"].max())+1,
        step=1,
        description="Split value:")
    sl2 = widgets.FloatSlider(
        value=10,
        min=min(df["load_capacity"].min(), df["age"].min())-1,
        max=max(df["load_capacity"].max(), df["age"].max())+1,
        step=1,
        description="Split value:")
    sl3 = widgets.FloatSlider(
        value=10,
        min=min(df["load_capacity"].min(), df["age"].min())-1,
        max=max(df["load_capacity"].max(), df["age"].max())+1,
        step=1,
        description="Split value:")
    # sl1.value=53
    # fd2.value='material_type'
    # check.value=True
    io=interactive_output(_split_feature, {'fd1':fd1,'fd2':fd2,'fd3':fd3,'check':check,'sl1':sl1,'sl2':sl2,'sl3':sl3,'df':fixed(df)})
    return VBox([HBox([fd1, sl1, check]), io, HBox([VBox([fd2,sl2]), VBox([fd3,sl3])])])

def _neural_network(step, show, check, predict, X, y, Xp):
    # this example adapted from 
    # https://iamtrask.github.io/2015/07/12/basic-python-network/
    # "A Neural Network in 11 lines of Python"
    def nonlin(x,deriv=False):
        if(deriv==True):
            return x*(1-x)
        return 1/(1+np.exp(-x))

    np.random.seed(1)

    # randomly initialize our weights with mean 0
    syn0 = 2*np.random.random((3,4)) - 1
    syn1 = 2*np.random.random((4,1)) - 1

    for j in np.arange(1+int(100*step)):

        # Feed forward through layers 0, 1, and 2
        l0 = X
        l1 = nonlin(np.dot(l0,syn0))
        l2 = nonlin(np.dot(l1,syn1))

        # how much did we miss the target value?
        l2_error = y - l2
        
        # if (j% 100) == 0:
        #     print("Error:" + str(np.mean(np.abs(l2_error))))
            
        # in what direction is the target value?
        # were we really sure? if so, don't change too much.
        l2_delta = l2_error*nonlin(l2,deriv=True)

        # how much did each l1 value contribute to the l2 error (according to the weights)?
        l1_error = l2_delta.dot(syn1.T)
        
        # in what direction is the target l1?
        # were we really sure? if so, don't change too much.
        l1_delta = l1_error * nonlin(l1,deriv=True)

        syn1 += l1.T.dot(l2_delta)
        syn0 += l0.T.dot(l1_delta)

    if predict:        
        l0p = Xp
        l1p = nonlin(np.dot(l0p,syn0))
        yp = nonlin(np.dot(l1p,syn1))[0][0]
        
    f,ax=plt.subplots(1,1, figsize=(8,4))
    ws=[None, syn0, syn1]
    cmap = plt.get_cmap("seismic")
    for i,n in enumerate([3,4,1]):
        ys=np.arange(n)
        ys=ys-np.mean(ys)
        ax.plot(0*ys+i, ys, 'ko', mfc='w', ms=40, zorder=2)

        if i == 0:
            yo=1*ys
            if predict:
                for xi,yi,ti in zip(0*ys+i, ys, Xp[0,:]):
                    ax.text(xi,yi,f'{ti:.1f}',ha='center',va='center', color='r')
            elif show>0:
                for xi,yi,ti in zip(0*ys+i, ys, X[show-1,:]):
                    ax.text(xi,yi,f'{ti:.1f}',ha='center',va='center')
            continue
        w=ws[i]
        for j,y1 in enumerate(yo):
            for k,y2 in enumerate(ys):
                c=w[j,k]/(2*np.max(abs(w)))+0.5
                if abs(c-0.5)<0.05:
                    c='k'
                    ls='--'
                else:
                    c=cmap(c)
                    ls='-'
                ax.plot([i-1,i], [y1,y2], ls, color=c, lw=abs(2*w[j,k])+0.25, zorder=1)
                
        if predict and i == 1:
            for yi,ti in zip(ys, l1p[0,:]):
                ax.text(1,yi,f'{ti:.3f}',ha='center',va='center',color='r')
        elif show>0 and i == 1:
            for yi,ti in zip(ys, l1[show-1,:]):
                ax.text(1,yi,f'{ti:.3f}',ha='center',va='center')
        yo=1*ys
    
    if predict:
        ax.text(2,0.,f'{yp:.2f}',ha='center',va='center', color='r')
    elif show>0:
        ax.text(2,-0.15,f'({y[show-1,0]:.2f})',ha='center',va='center', alpha=0.6)
        ax.text(2,0.15,f'{l2[show-1,0]:.2f}',ha='center',va='center')
    ax.set_xlim(-0.6, 2.6)
    ax.set_ylim(-2.1, 2.6)

    if check:
        ax.text(0, 2.5, 'input\nlayer\n(features)', style='italic', ha='center', va='top')
        ax.text(1, 2.5, 'hidden\nlayer', style='italic', ha='center', va='top')
        ax.text(2, 2.5, 'output\nlayer\n(label)', style='italic', ha='center', va='top')
        
        xi=-0.3
        ax.text(xi, -1, 'current\nrainfall', style='italic', ha='right', va='center')
        ax.text(xi, 0, 'previous\nrainfall', style='italic', ha='right', va='center')
        ax.text(xi, 1, 'previous\nrunoff', style='italic', ha='right', va='center')
        ax.text(2-xi, 0, 'current\nrunoff', style='italic', ha='left', va='center')

    ax.text(2, -1., f'training\nerror\n={np.mean(np.abs(l2_error)):.2f}', ha='center', va='top')

    ax.axis('off')
    plt.show()
    return

def neural_network(X,y,Xp):    
    step = widgets.IntSlider(value=0, min=0, max=10, step=1, description="training steps")
    show = widgets.IntSlider(value=0, min=0, max=4, step=1, description="show datapoint")
    check = Checkbox(value=False, description="labels")
    predict = Checkbox(value=False, description="predict")
    io=interactive_output(_neural_network, {'step':step, 'show':show, 'check':check, 'predict':predict, 'X':fixed(X), 'y':fixed(y), 'Xp':fixed(Xp)})
    return VBox([HBox([VBox([step, show]), VBox([check, predict])]), io])