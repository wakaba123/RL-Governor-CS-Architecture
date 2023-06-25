//package com.example.networktrans;
//
//import static java.lang.Math.max;
//import static java.lang.Math.round;
//
//import org.checkerframework.checker.units.qual.A;
//
//import java.util.ArrayList;
//import java.util.Arrays;
//import java.util.Collections;
//import java.util.Objects;
//import java.util.stream.Collectors;
//
//public class Scheduler {
//    private int interval = 5;
//    private int pmu_num = 2;
//    private int thread_num;
//    private ArrayList<Double> priority_arr = new ArrayList<>();
//    private ArrayList<ArrayList<Integer>> main_pmu_data = new ArrayList<>();
//    private ArrayList<ArrayList<Integer>> render_pmu_data = new ArrayList<>();
//    private ArrayList<ArrayList<Integer>> sf_pmu_data = new ArrayList<>();
//    private ArrayList<ArrayList<Integer>> all_pmu_data = new ArrayList<>();
//    private ArrayList<Double> commu_info = new ArrayList<>();
//
//    private int [] inst_min = {18700000, 155000000, 27700000};
//    private int [] task_clock_max_little = {122, 400, 131};
//    private int [] task_clock_max_big = {64, 400, 130};
//
//    private int [] task_clock_min_little = {94, 212, 104};
//    private int [] task_clock_min_big = {64, 467, 105};
//
//    private ArrayList<Integer> tid_list = new ArrayList<>();
//    private String tid_list_str;
//
//
//    private int big_scale = 0;
//    private int little_scale= 0;
//    private int big_scale_freq_idx = 0;
//    private int little_scale_freq_idx = 0;
//    private int big_scale_freq;
//    private int little_scale_freq;
//
//    private int [] big_freq_list;
//    private int [] little_freq_list;
//
//    private double big_priority = 0;
//    private double little_priority = 1;
//    private int [] position_bit = {1,1,0};
//
//    public Scheduler(String tid_list_str, int[] big_freq_list, int[] little_freq_list){
//        this.tid_list_str = tid_list_str;
//        for(final String value: tid_list_str.split(",")){
//            this.tid_list.add(Integer.parseInt(value));
//        }
//        thread_num = tid_list.size();
//
//        this.big_freq_list =  big_freq_list;
//        this.little_freq_list = little_freq_list;
//
//        initArrayList(all_pmu_data,10);
//        initArrayList(main_pmu_data,10);
//        initArrayList(sf_pmu_data,10);
//        initArrayList(render_pmu_data,10);
//
//
//        for(int i = 0; i < thread_num; i++){
//            String command = "taskset -ap ff " + tid_list.get(i);
//            CommandExecution.easyExec(command,true);
//        }
//
//        for(int i = 0; i < thread_num; i++){
//            String command;
//            if(position_bit[i] == 1){
//                command = "taskset -p f0 " + tid_list.get(i);
//            } else {
//                command = "taskset -p 0f " + tid_list.get(i);
//            }
//            CommandExecution.easyExec(command,true);
//        }
//    }
//    public  ArrayList<Double> schedule(int big_current_freq, int little_current_freq){
//        big_scale = 0;
//        little_scale = 0;
//        big_scale_freq_idx = 0;
//        little_scale_freq_idx = 0;
//        String command = "simpleperf stat -e task-clock,instructions -t " + tid_list_str + " --duration 1 --per-thread";
//        String result = CommandExecution.execCommand(command,true).successMsg;
//        String []  result_array = result.split("\n");
//        result_array = Arrays.copyOfRange(result_array,3,result_array.length);
//
//        if(result_array.length!=8){
//            commu_info.add(big_priority);
//            commu_info.add(little_priority);
//            commu_info.add((double)big_scale);
//            commu_info.add((double)big_scale_freq_idx);
//            commu_info.add((double)little_scale);
//            commu_info.add((double)little_scale_freq_idx);
//            return commu_info;
//        }
//        int pmu;
//        int i;
//        for(i = 0; i < pmu_num;i++) {
//            String thread_name = result_array[i * thread_num].split("\\s+")[1];
//            if (result_array[i * thread_num].contains("(ms)")) {
//                pmu = Integer.parseInt(result_array[i * thread_num].split("\\s+")[4].split("\\.")[0].replace(",", ""));
//            } else {
//                pmu = Integer.parseInt(result_array[i * thread_num].split("\\s+")[4].replace(",", ""));
//            }
//            if (Objects.equals(thread_name, "droid.ugc.aweme")) {
//                main_pmu_data.get(i).add(pmu);
//                all_pmu_data.get(0).add(pmu);
//            } else if (Objects.equals(thread_name, "RenderThread")) {
//                render_pmu_data.get(i).add(pmu);
//                all_pmu_data.get(1).add(pmu);
//            } else {
//                sf_pmu_data.get(i).add(pmu);
//                all_pmu_data.get(2).add(pmu);
//            }
//
//            thread_name = result_array[i * thread_num + 1].split("\\s+")[1];
//            if (result_array[i * thread_num + 1].contains("(ms)")) {
//                pmu = Integer.parseInt(result_array[i * thread_num + 1].split("\\s+")[4].split("\\.")[0].replace(",", ""));
//            } else {
//                pmu = Integer.parseInt(result_array[i * thread_num + 1].split("\\s+")[4].replace(",", ""));
//            }
//            if (Objects.equals(thread_name, "droid.ugc.aweme")) {
//                main_pmu_data.get(i).add(pmu);   // TODO 不一定可以
//                all_pmu_data.get(0).add(pmu);
//            } else if (Objects.equals(thread_name, "RenderThread")) {
//                render_pmu_data.get(i).add(pmu);
//                all_pmu_data.get(1).add(pmu);
//            } else {
//                sf_pmu_data.get(i).add(pmu);
//                all_pmu_data.get(2).add(pmu);
//            }
//
//            thread_name = result_array[i * thread_num + 2].split("\\s+")[1];
//            if (result_array[i * thread_num + 2].contains("(ms)")) {
//                pmu = Integer.parseInt(result_array[i * thread_num + 2].split("\\s+")[4].split("\\.")[0].replace(",", ""));
//            } else {
//                pmu = Integer.parseInt(result_array[i * thread_num + 2].split("\\s+")[4].replace(",", ""));
//            }
//            if (Objects.equals(thread_name, "droid.ugc.aweme")) {
//                main_pmu_data.get(i).add(pmu);
//                all_pmu_data.get(0).add(pmu);
//            } else if (Objects.equals(thread_name, "RenderThread")) {
//                render_pmu_data.get(i).add(pmu);
//                all_pmu_data.get(1).add(pmu);
//            } else {
//                sf_pmu_data.get(i).add(pmu);
//                all_pmu_data.get(2).add(pmu);
//            }
//        }
//
//        for(int i1 = 0; i1 < thread_num; i1++){
//            priority_arr.add(all_pmu_data.get(i1).get(0) / 1000.0);
//        }
//
//        little_priority = 0;
//        big_priority = 0;
//
//        for(int i1 = 0; i1 < thread_num; i1++){
//            if(position_bit[i1] == 0){
//                little_priority = little_priority + priority_arr.get(i1);
//            }else{
//                big_priority = big_priority + priority_arr.get(i1);
//            }
//        }
//
//        ArrayList<Double> a = (ArrayList<Double>) priority_arr.clone();
//        ArrayList<Integer> sort_index = argsort(a);
//        Collections.reverse(sort_index);
//
//        int[] big_scale_arr = {0,0,0};
//        int[] little_scale_arr = {0,0,0};
//        int[] big_scale_freq_arr = {0,0,0};
//        int[] little_scale_freq_arr = {0,0,0};
//
//        for(i = 0; i < sort_index.size(); i++){
//            int index = sort_index.get(i);
//            int task_clock = all_pmu_data.get(index).get(0);
//            int inst = all_pmu_data.get(index).get(1);
//            int big_scale_freq = 0;
//            int little_scale_freq= 0;
//
//            if(inst > inst_min[index]){
//                if(position_bit[index] == 1 && task_clock < task_clock_min_big[index]){
//                    big_scale_freq = big_freq_list[big_freq_list.length-1];
//                    for(int j = big_freq_list.length -1; j >=0; j--){
//                        int big_freq = big_freq_list[index];
//                        if(big_freq / big_current_freq < task_clock / task_clock_min_big[index]){
//                            big_scale_freq = big_freq;
//                            break;
//                        }
//                    }
//                    if(big_scale_freq == big_freq_list[big_freq_list.length - 1]){
//                       little_priority = little_priority + priority_arr.get(index);
//                       big_priority = big_priority - priority_arr.get(index);
//                       position_bit[index] = 0;
//                       command = "taskset -p 0f "+Integer.toString(tid_list.get(index));
//                       CommandExecution.easyExec(command,true);
//                       break;
//                    }else {
//                        big_scale_arr[i] = -1;
//                        big_scale_freq_arr[i] = big_scale_freq;
//                    }
//
//                } else if(0 == position_bit[index] && task_clock < task_clock_min_little[index]){ //250
//                    little_scale_arr[i] = -1;
//                    little_scale_freq = little_freq_list[little_freq_list.length - 1];
//                    for(int j = little_freq_list.length-1; j >= 0; j--){
//                        int little_freq = little_freq_list[j];
//                        if(little_freq / little_current_freq < task_clock / task_clock_min_little[index]){
//                            little_scale_freq = little_freq;
//                            break;
//                        }
//                    }
//                    if(little_scale_freq == little_freq_list[little_freq_list.length - 1]){
//                        little_scale_freq_arr[i] = little_freq_list[0];
//                    }else{
//                        little_scale_freq_arr[i] = little_scale_freq;
//                    }
//                } else if(position_bit[index] == 1 && task_clock > task_clock_max_big[index]){
//                    big_scale_arr[i] = 1;
//                    big_scale_freq = big_freq_list[0];
//                    for(final  int big_freq : big_freq_list){
//                        if(big_freq / big_current_freq > task_clock / task_clock_max_big[index]){
//                            big_scale_freq = big_freq;
//                            break;
//                        }
//                    }
//                    if (big_scale_freq == big_freq_list[0]){
//                        big_scale_freq_arr[i] = big_freq_list[big_freq_list.length - 1];
//                    } else {
//                        big_scale_freq_arr[i] = big_scale_freq;
//                    }
//                } else if(position_bit[index] == 0 && task_clock < task_clock_min_little[index]){
//                    little_scale_freq = little_freq_list[0];
//                    for(final int little_freq:little_freq_list){
//                        if(little_freq / little_current_freq > task_clock / task_clock_max_little[index]){
//                            little_scale_freq = little_freq;
//                            break;
//                        }
//                    }
//                    if(little_scale_freq == little_freq_list[0]){
//                        big_priority = big_priority + priority_arr.get(index);
//                        little_priority = little_priority - priority_arr.get(index);
//                        position_bit[index]= 1;
//                        command = "taskset -p f0" + tid_list.get(index);
//                        result = CommandExecution.execCommand(command,true).successMsg;
//                        break;
//                    } else {
//                        little_scale_arr[i] = 1;
//                        little_scale_freq_arr[i] = little_scale_freq;
//                    }
//                }
//            } else if(inst < inst_min[index]){  // 310
//                if(position_bit[index] == 0){
//                    little_scale_freq = little_freq_list[0];
//                    for(final int little_freq:little_freq_list){
//                        if(little_freq / little_current_freq > inst_min[index] / inst){
//                            little_scale_freq = little_freq;
//                            break;
//                        }
//                    }
//                    if(little_scale_freq == little_freq_list[0]){
//                        big_priority = big_priority + priority_arr.get(index);
//                        little_priority = little_priority - priority_arr.get(index);
//                        position_bit[index] = 1;
//                        command = "taskset -p f0 " + Integer.toString(tid_list.get(index));
//                        CommandExecution.execCommand(command,true);
//                        break;
//                    } else {
//                        little_scale_arr[i] = 1;
//                        little_scale_freq_arr[i] = little_scale_freq;
//                    }
//                }else{
//                    big_scale_arr[i] = 1;
//                    big_scale_freq = big_freq_list[0];
//                    for(final int big_freq: big_freq_list){
//                        if(big_freq / big_current_freq > inst_min[index] / inst){
//                            big_scale_freq = big_freq;
//                            break;
//                        }
//                    }
//                    if(big_scale_freq == big_freq_list[0]){
//                        big_scale_freq_arr[i] = big_freq_list[big_freq_list.length - 1];
//                    }else {
//                        big_scale_freq_arr[i] = big_scale_freq;
//                    }
//                }
//            }
//        }
//
//        int down_max_freq = big_freq_list[0];
//        int min_freq = big_freq_list[big_freq_list.length-1];
//        int max_freq = big_freq_list[0];
//        boolean up_bool = false;
//        boolean down_bool = false;
//        for(int i1 = 0; i1 < big_scale_arr.length; i1++){
//            if(big_scale_arr[i1] == 1){
//                max_freq = max(max_freq, big_scale_freq_arr[i1]);
//                up_bool = true;
//            }else if(big_scale_arr[i1] == -1){
//                down_max_freq = max(down_max_freq, big_scale_freq_arr[i1]);
//                down_bool = true;
//            }
//        }
//
//        if(up_bool){
//            big_scale = 1;
//            big_scale_freq = max_freq;
//        }else if(down_bool){
//            big_scale=  -1;
//            big_scale_freq = down_max_freq;
//        }
//
//        down_max_freq = little_freq_list[0];
//        min_freq = little_freq_list[little_freq_list.length - 1];
//        max_freq = little_freq_list[0];
//        up_bool = false;
//        down_bool = false;
//
//
//        for(int i1 = 0 ; i1 < little_scale_arr.length; i1++){
//            if(little_scale_arr[i1] == 1){
//                max_freq = max(max_freq, little_scale_freq_arr[i1]);
//                up_bool = true;
//            } else if(little_scale_arr[i1] == -1){
//                down_max_freq = max(down_max_freq, little_scale_freq_arr[i1]);
//                down_bool = true;
//            }
//        }
//        if(up_bool){
//            little_scale = 1;
//            little_scale_freq = max_freq;
//        }
//        if(down_bool){
//            little_scale = -1;
//            little_scale_freq = down_max_freq;
//        }
//
//        if(big_scale != 0){
//            for(int i1 = 0; i1 < big_freq_list.length; i1++){
//                if(big_freq_list[i1] == big_scale_freq){
//                    big_scale_freq_idx = i1;
//                }
//            }
//        }
//        if(little_scale != 0){
//            for(int i1 =0 ; i1< little_freq_list.length; i1++){
//                if(little_freq_list[i1] == little_scale_freq){
//                    little_scale_freq_idx = i1;
//                }
//            }
//        }
//
//        commu_info.add(big_priority);
//        commu_info.add(little_priority);
//        commu_info.add((double)big_scale);
//        commu_info.add((double)big_scale_freq_idx);
//        commu_info.add((double)little_scale);
//        commu_info.add((double)little_scale_freq_idx);
//
//        return commu_info;
//    }
//
//    private ArrayList<Integer> argsort(ArrayList<Double> input) {
//            int h = input.size();
//            ArrayList<Integer> index = new ArrayList<>();
//
//            for (int i = 0; i < h; ++i)
//                index.add(i);
//
//            for (int i = h - 1; i > 0; --i)
//            {
//                int min = 0;
//                for (int j = 1; j <= i; ++j)
//                    if (input.get(index.get(j)) < input.get(index.get(min)))
//                        min = j;
//
//                int temp = index.get(i);
//                index.set(i, index.get(min));
//                index.set(min, temp);
//            }
//            return index;
//    }
//
//    private void initArrayList(ArrayList<ArrayList<Integer>> a, int num){
//        for(int i  = 0; i < num; i++){
//            ArrayList<Integer> temp = new ArrayList<>();
//            a.add(temp);
//        }
//    }
//}
