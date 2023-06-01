package com.example.networktrans;

import static java.lang.Math.max;
import static java.lang.Math.min;

public class CPUFreqSetting {
    private static final int [] littleChoice = Config.allowedLittleFrequencies;
    private static final int [] bigChoice = Config.allowedBigFrequencies;
    private static final int [] sbigChoice = Config.allowedSBigFrequencies;

    public static void setFreq(int choice) throws Exception {
        choice = min(choice, Config.maxFrequencyChoices - 1);
        choice = max(0, choice);

        int bigFreq = bigChoice[choice / 3 % 3];
        int littleFreq = littleChoice[choice % 3];
        int sbigFreq = sbigChoice[choice / 3 / 3];

        String response = null;
        String TAG = "CPUFreqSetting";

        ServerUtil.sendSocket("0" + " " + sbigFreq + " " + bigFreq + " " + littleFreq);
    }
}
