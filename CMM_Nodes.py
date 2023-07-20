# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 07:50:59 2023

@author: jan.devreugd@tno.nl
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import streamlit as st
import plotly.graph_objects as go
import pyperclip

def funcAsphere(x,y,RoC,conic):
    R = np.sqrt(x**2+y**2)
    asphereZ = R**2 / ( RoC * ( 1 + np.sqrt( 1 - (1+conic) * (R/RoC)**2  ) ) ) 
    return asphereZ  

def plotly_function(x,y,title):
    fsize = 18
    
    fig=go.Figure()
    fig = fig.add_trace(go.Scatter(x=x,y=y,mode = 'markers'))
    fig.update_layout(title_text=title, title_x=0.5,title_font_size=22)
    fig.update_layout(xaxis = dict(tickfont = dict(size=fsize)))
    fig.update_xaxes(title_font_size=fsize)
    fig.update_layout(yaxis = dict(tickfont = dict(size=fsize)))
    fig.update_yaxes(title_font_size=fsize)
    fig.update_layout(width=1000, height=1000)
    fig = fig.update_xaxes(title_text = 'X-coordinates')
    fig = fig.update_yaxes(title_text = 'Y-coordinates')
    fig.update_layout(legend = dict(font = dict(size = fsize, color = "black")))
    st.plotly_chart(fig,use_container_width=False)
    
def PlotContour(x,y,z,title):

    fig, ax = plt.subplots(figsize=(10, 8))
    p1 = ax.tripcolor(x,y,z,cmap=plt.cm.jet, shading='gouraud')
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.title(title)
    ax.set_aspect('equal', 'box')
    fig.colorbar(p1)
    plt.scatter(x, y, color='black', s=2)
    plt.tight_layout()
    st.pyplot(plt)  
    
def PlotContour2(x, y, z, title):
    # Create the contour plot
    fig = go.Figure()

    # Add the contour plot
    fig.add_trace(go.Contour(x=x, y=y, z=z, colorscale='Jet', colorbar=dict(title='Z values')))

    # Add black dots at each data point
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers', marker=dict(size=3, color='black')))

    # Customize the layout
    fig.update_layout(title=title, xaxis_title='x [m]', yaxis_title='y [m]',
                      showlegend=False)  # Hide legend for the black dots

    # Show the plot
    st.plotly_chart(fig, use_container_width=True)

    # Show the plot
    st.plotly_chart(fig, use_container_width=True)    

def main():
    
    with st.sidebar:
        st.title('CMM nodes for facesheet measurements')
        st.write('info: jan.devreugd@tno.nl')
        
        RoC = st.number_input('Radius of Curvature [meters]:',value = -4.19818, format='%.5f', step = 0.001)
        conic = st.number_input('conical constant [-]:',value = -3.604, format='%.4f', step = 0.001)
        Rout = st.number_input('Outer radius mirror [mm]:',value = 0.302, format='%.3f', step = 0.001)
        n_rings = st.number_input('number of rings [-]:',value = 10, step=1,max_value=70)
        
        pitch = Rout/n_rings
        
        st.write(f'the pitch is {1000*pitch:2f} [mm]')
        
        r = 0
        x = np.array([])
        y = np.array([])
        for j in range(1,n_rings+1):
            r = r + pitch
            nact = 6*j
            theta_offset = 0.0
            for k in range(1,nact+1):
                phi = np.pi*2/(nact)*(k + theta_offset)
                x = np.append(x,r*np.cos(phi))
                y = np.append(y,r*np.sin(phi))
                
        R = np.sqrt(x**2 + y**2)
        Z = funcAsphere(x, y, RoC, conic)
        
        factor = -1
        #factors = 1
        
        Z1X = factor*(2*x/(RoC*(np.sqrt(1 - (conic + 1)*(x**2 + y**2)/RoC**2) + 1)) + x*(conic + 1)*(x**2 + y**2)/(RoC**3*np.sqrt(1 - (conic + 1)*(x**2 + y**2)/RoC**2)*(np.sqrt(1 - (conic + 1)*(x**2 + y**2)/RoC**2) + 1)**2))
        Z1Y = factor*(2*y/(RoC*(np.sqrt(1 - (conic + 1)*(x**2 + y**2)/RoC**2) + 1)) + y*(conic + 1)*(x**2 + y**2)/(RoC**3*np.sqrt(1 - (conic + 1)*(x**2 + y**2)/RoC**2)*(np.sqrt(1 - (conic + 1)*(x**2 + y**2)/RoC**2) + 1)**2))
        Z1Z = factor*(-1*np.ones((len(x))))
        VL = np.sqrt(Z1X**2+Z1Y**2+Z1Z**2)
        
        Z1X = Z1X/VL
        Z1Y = Z1Y/VL
        Z1Z = Z1Z/VL
        
        my_array = np.array([1000*x,1000*y,1000*Z,Z1X,Z1Y,Z1Z]).T
        
        
        
        st.write(f'the number of nodes = {len(x)}')
        
        
    #plotly_function(x, y, 'CMM nodes')
    PlotContour(x, y, Z, f'{len(x)} datapoints, pitch is {1000*pitch:.2f} [mm]\n RoC = {RoC}, kappa = {conic}, max Radius = {Rout}')


    # Display the array using Streamlit with the header
    with st.expander('data points', expanded=False): 
        df = pd.DataFrame(my_array, columns=['x', 'y', 'z','e1','e2','e3'])
        st.table(df)

    # Add a button to save the array to the clipboard
    if st.button("Copy data points to Clipboard"):
        copy_array_to_clipboard(df)
        st.write("CMM input data is copied to the clipboard.")

def copy_array_to_clipboard(df):
    # Convert the DataFrame to a string representation (tab-separated values)
    array_str = df.to_csv(index=False, sep='\t')

    # Copy the array content to the clipboard
    pyperclip.copy(array_str)

if __name__ == "__main__":
    main()
