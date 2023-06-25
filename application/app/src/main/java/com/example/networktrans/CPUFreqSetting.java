package com.example.networktrans;

import static java.lang.Math.max;
import static java.lang.Math.min;

public class CPUFreqSetting {
    private static final int [] littleChoice = Config.allowedLittleFrequencies;
    private static final int [] bigChoice = Config.allowedBigFrequencies;

    public static void setFreq(int choice, int choice2 ) throws Exception {  // choice2为coordinator的choice
        if(choice2 != -1){
            choice2 = min(choice2, Config.maxFrequencyChoices - 1);
            choice2 = max(0, choice2);
        }

        int bigFreq = bigChoice[max(choice / 4 , choice2/ 4)];
        int littleFreq = littleChoice[max(choice % 4, choice2 % 4)];

        String response = null;
        String TAG = "CPUFreqSetting";

        ServerUtil.sendSocket("0" + " " + bigFreq + " " + littleFreq);
    }
}
