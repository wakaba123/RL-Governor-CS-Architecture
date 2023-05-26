package com.example.networktrans;

import static java.lang.Math.max;
import static java.lang.Math.min;

import java.util.ArrayList;
import java.util.Arrays;

public class Coordinator {
    private int[] big_freq_list;
    private int[] little_freq_list;

    public Coordinator(int [] big_freq_list, int []little_freq_list){
        this.big_freq_list = big_freq_list;
        this.little_freq_list = little_freq_list;
    }

    public int getArrayIndex(int[] arr,int value) {

        int k=0;
        for(int i=0;i<arr.length;i++){

            if(arr[i]==value){
                k=i;
                break;
            }
        }
        return k;
    }

    public double[] coordinate(ArrayList<Double> commu_info , double big_util, double little_util, int big_current_freq, int little_current_freq){
        int big_scale_EFC = 0;
        int little_scale_EFC = 0;
        double big_priority = commu_info.get(0);
        double little_priority = commu_info.get(1);
        if(big_util >= 3 || big_priority >= 0.75){
            big_scale_EFC = 1;
        }
        if(big_util < 1.75 && big_priority <0.25){
            big_scale_EFC = -1;
        }
        if(little_util >= 2.75 || little_priority >= 1.2){
            little_scale_EFC = 1;
        }
        if(little_util < 1.75 && little_priority < 0.4){
            little_scale_EFC = -1;
        }
        int big_scale_freq_EFC = getArrayIndex(big_freq_list, big_current_freq) + big_scale_EFC * 2;
        int little_scale_freq_EFC = getArrayIndex(little_freq_list,little_current_freq) + little_scale_EFC * 2;

        double big_scale, little_scale;
        int big_scale_freq_idx, little_scale_freq_idx;
        if(commu_info.get(2) != 0){
            big_scale = commu_info.get(2);
            big_scale_freq_idx = commu_info.get(3).intValue();
            if(big_scale_freq_idx % 2 == 0){
                big_scale_freq_idx = big_scale_freq_idx + commu_info.get(2).intValue();
            }
        } else {
            big_scale = big_scale_EFC;
            big_scale_freq_idx = big_scale_freq_EFC;
        }
        if(commu_info.get(4) != 0){
            little_scale = commu_info.get(4);
            little_scale_freq_idx = commu_info.get(5).intValue();
            if(little_scale_freq_idx % 2 == 0){
                little_scale_freq_idx = little_scale_freq_idx + commu_info.get(4).intValue();
            }
        }else{
            little_scale = little_scale_EFC;
            little_scale_freq_idx = little_scale_freq_EFC;
        }
        big_scale_freq_idx = min(6, big_scale_freq_idx);
        little_scale_freq_idx = min(6, little_scale_freq_idx);
        big_scale_freq_idx = max(0, big_scale_freq_idx);
        little_scale_freq_idx = max(0, little_scale_freq_idx );
        return new double[] {big_scale, big_scale_freq_idx, little_scale, little_scale_freq_idx};

    }

}
