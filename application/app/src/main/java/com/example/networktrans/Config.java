package com.example.networktrans;

public class Config {
    public static final String BinaryServerPosition = "/data/local/tmp/server";
    public static final String SERVER_IP = "127.0.0.1";
    public static final int SERVER_PORT = 8888;
    public static final String view = "com.smile.gifmaker/com.yxcorp.gifshow.HomeActivity#0";
    public static final int ModelInputNum = 6;
    public static final int ModelActionNum = 27;
    public static final int TargetFPS = 120;
    public static final String ModelName = "model_oneplus9pro.tflite";

    public static final int ClusterNum = 3;


    /*
    public static final int maxFrequencyChoices = 16;
    // 300000 403200 480000 576000 652800 748800 825600 902400 979200 1056000 1132800 1228800 1324800 1420800 1516800 1612800 1689600 1766400
    public static final int [] allowedBigFrequencies = {748800,1056000,1420800,1766400} ;
    // 825600 902400 979200 1056000 1209600 1286400 1363200 1459200 1536000 1612800 1689600 1766400 1843200 1920000 1996800 2092800 2169600 2246400 2323200 2400000 2476800 2553600 2649600
    public static final int [] allowedLittleFrequencies = {1459200, 1843200, 2246400, 2649600 };
    */

    //300000 403200 499200 595200 691200 806400 902400 998400 1094400 1209600 1305600 1401600 1497600 1612800 1708800 1804800
    public static final int [] allowedLittleFrequencies = {806400, 1305600, 1804800};
    //710400 844800 960000 1075200 1209600 1324800 1440000 1555200 1670400 1766400 1881600 1996800 2112000 2227200 2342400 2419200
    public static final int [] allowedBigFrequencies = {1324800, 1881600, 2419200} ;
    //844800 960000 1075200 1190400 1305600 1420800 1555200 1670400 1785600 1900800 2035200 2150400 2265600 2380800 2496000 259200 2680000 2764880 2841600
    public static final int [] allowedSBigFrequencies = {1555200, 2265600, 2841600} ;

    public static final int maxFrequencyChoices = 27;
}
