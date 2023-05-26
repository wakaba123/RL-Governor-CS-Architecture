package com.example.networktrans;

public class Config {
    public static final String BinaryServerPosition = "/data/local/tmp/server";
    public static final String SERVER_IP = "127.0.0.1";
    public static final int SERVER_PORT = 8888;
    public static final String view = "com.smile.gifmaker/com.yxcorp.gifshow.HomeActivity#0";
    // 300000 403200 480000 576000 652800 748800 825600 902400 979200 1056000 1132800 1228800 1324800 1420800 1516800 1612800 1689600 1766400
    public static final int [] allowedBigFrequencies = {748800,1056000,1420800,1766400} ;

    // 825600 902400 979200 1056000 1209600 1286400 1363200 1459200 1536000 1612800 1689600 1766400 1843200 1920000 1996800 2092800 2169600 2246400 2323200 2400000 2476800 2553600 2649600
    public static final int [] allowedLittleFrequencies = {1459200, 1843200, 2246400, 2649600 };

    public static final int maxFrequencyChoices = 16;


}
