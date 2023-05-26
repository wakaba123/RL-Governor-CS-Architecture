package com.example.networktrans;

import static java.lang.Math.max;
import static java.lang.Math.min;

public class CPUFreqSetting {
    private static final int [] littleChoice = Config.allowedLittleFrequencies;
    private static final int [] bigChoice = Config.allowedBigFrequencies;

    public static void setFreq(int choice) throws Exception {
        choice = min(choice, Config.maxFrequencyChoices - 1);
        choice = max(0, choice);

        int bigFreq = bigChoice[choice / 4];
        int littleFreq = littleChoice[choice % 4];

        String response = null;
        String TAG = "CPUFreqSetting";

        ServerUtil.sendSocket("0" + " " + bigFreq + " " + littleFreq);
    }
}
