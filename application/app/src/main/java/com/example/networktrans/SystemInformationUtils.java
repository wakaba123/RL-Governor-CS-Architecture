package com.example.networktrans;

import static java.lang.Double.max;

import android.util.Log;

import org.checkerframework.checker.units.qual.A;

import java.util.ArrayList;
import java.util.concurrent.ConcurrentMap;


public class SystemInformationUtils {
    public SystemInformationUtils(){
    }

    public static String getCurrentFocusWindow(){
        String str = CommandExecution.execCommand("dumpsys window | grep mCurrentFocus",true).successMsg;
        String [] strSplited = str.split(" ");
        int n = strSplited.length;
        return strSplited[n-1].substring(0, strSplited[n-1].length()-2);
    }

    public static String getCurrentForegroundAppPid(){
        String str = CommandExecution.execCommand("dumpsys window | grep mCurrentFocus", true).successMsg;
        String [] strSplited = str.split(" ");
        int n = strSplited.length;
        String activityName = strSplited[n-1].substring(0, strSplited[n-1].length()-2);
        String packageName =  activityName.substring(0, activityName.indexOf("/"));
        str = CommandExecution.execCommand("pidof " + packageName, true).successMsg;
        str = str.substring(0, str.length() - 1);
        return str;
    }

    public static String getRenderThreadTid(String pid){
        String str = CommandExecution.execCommand("ps -T -p " + pid + " | grep RenderThread", true).successMsg;
        String [] strSplited = str.split("\\s+");
        String tid = strSplited[2];
        return tid;
    }

    public static String getSurfaceFlinger(){
        String str = CommandExecution.execCommand("pidof surfaceflinger", true).successMsg;
        return str.substring(0, str.length() - 1);
    }

    public static void setGovernorToUserSpace(){
        String command = "echo \"userspace\" >  /sys/devices/system/cpu/cpufreq/policy0/scaling_governor"; // little cpu governor
        CommandExecution.easyExec(command,true);
        command = "echo \"userspace\" >  /sys/devices/system/cpu/cpufreq/policy4/scaling_governor";  // big cpu governor
        CommandExecution.easyExec(command,true);
        command = "echo \"userspace\" >  /sys/devices/system/cpu/cpufreq/policy7/scaling_governor";  // big cpu governor
        CommandExecution.easyExec(command,true);
    }
    public static void initGovernor(){
        String command = "echo \"schedutil\" >  /sys/devices/system/cpu/cpufreq/policy0/scaling_governor"; // little cpu governor
        CommandExecution.easyExec(command,true);
        command = "echo \"schedutil\" >  /sys/devices/system/cpu/cpufreq/policy4/scaling_governor";  // big cpu governor
        CommandExecution.easyExec(command,true);
        command = "echo \"schedutil\" >  /sys/devices/system/cpu/cpufreq/policy7/scaling_governor";  // big cpu governor
        CommandExecution.easyExec(command,true);
    }

}
