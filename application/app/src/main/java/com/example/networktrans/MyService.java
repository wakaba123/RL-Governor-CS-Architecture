package com.example.networktrans;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;
import android.widget.Toast;

import androidx.core.app.NotificationCompat;

import org.tensorflow.lite.DataType;
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Objects;

public class MyService extends Service {
    private TFLiteClassificationUtil tfLiteClassificationUtil;

    TensorBuffer x = TensorBuffer.createDynamic(DataType.FLOAT32);
    TensorBuffer y = TensorBuffer.createDynamic(DataType.FLOAT32);
    private int last_choice = -1;
    String TAG = "MyService";
    public static final String CHANNEL_ID = "ForegroundServiceChannel";
    SystemInformationUtils systemInformationUtils;
    MyService.SchedulerAndGovernorThread sit;


    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String input = intent.getStringExtra("inputExtra");
        createNotificationChannel();
        Intent notificationIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(this,
                0, notificationIntent, PendingIntent.FLAG_IMMUTABLE);
        Notification notification = new NotificationCompat.Builder(this, CHANNEL_ID)
                .setContentTitle("Foreground Service")
                .setContentText(input)
                .setSmallIcon(R.mipmap.ic_launcher)
                .setContentIntent(pendingIntent)
                .build();
        startForeground(1, notification);
        return START_NOT_STICKY;
    }

    @Override
    public void onCreate() {
        super.onCreate();

        Context context = getApplicationContext();
        Intent intent = new Intent(context, MyService.class);
        context.startForegroundService(intent);

        try {                                                // 这部分载入模型
            long t1 = System.currentTimeMillis();
            loadModel();
            long t2 = System.currentTimeMillis();
            Log.d(TAG, "load model takes " + (t2 - t1) + " ms");
        } catch (Exception e) {
            e.printStackTrace();
        }

//        SystemInformationUtils.setGovernorToPerformance();

        try {
            sit = new SchedulerAndGovernorThread(Config.view);    // 启动调频的线程
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        sit.start();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        SystemInformationUtils.initGovernor();
        ServerUtil.stopServer();

        sit.setStop();
        sit.interrupt();
        try {
            sit.join();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        Log.d(TAG, "Service and Thread destroyed");

    }

    @Override
    public IBinder onBind(Intent intent) {
        // TODO: Return the communication channel to the service.
        return null;
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel serviceChannel = new NotificationChannel(
                    CHANNEL_ID,
                    "Foreground Service Channel",
                    NotificationManager.IMPORTANCE_DEFAULT
            );
            NotificationManager manager = getSystemService(NotificationManager.class);
            manager.createNotificationChannel(serviceChannel);
        }
    }

    public class SchedulerAndGovernorThread extends Thread {
        private String view;
        private boolean check = false;
        private boolean isStop = false;

        public SchedulerAndGovernorThread(String view) throws InterruptedException {
            this.view = view;
        }

        public void setStop() {
            isStop = true;
        }

        public boolean checkView() {  // result 1 means not correct , result 0 means correct
            String result = ServerUtil.sendSocket("5 " + view);
            return !Objects.equals(result, "1");
        }

        @Override
        public void run() {
            while (!isStop) {

                while(!check){  // 进行整个的检查

                    while (!ServerUtil.checkServerAlive1()) {  // 检查server是否正常
                        try {
                            Thread.sleep(1000);
                        } catch (InterruptedException e) {
                            throw new RuntimeException(e);
                        }
                        Log.d(TAG, "check whether server is running " + view);
                    }
                    // 能出循环说明server正常

                    while (!checkView()) {    // 检查当前view
                        try {
                            Thread.sleep(1000);
                        } catch (InterruptedException e) {
                            throw new RuntimeException(e);
                        }
                        Log.d(TAG, "current view is not right, expected view is " + view);
                    }
                    // 能出循环说明当前的view正确
                    check = true;
                }

                try {                                       // 开始进行调频和调度
                    Thread.sleep(1000);
                    long t1 = System.currentTimeMillis();
                    Log.d(TAG, "===========begin==============");
                    calculate();                            // 使用模型计算下一次的频率以及设置频率
                    Log.d(TAG, "===========over==============");
                    long t2 = System.currentTimeMillis();
                    Log.d(TAG, "total time takes " + (t2 - t1) + " ms");
                } catch (Exception e) {
                    check = false;
                    Log.d(TAG, "Unkown Error");
                    e.printStackTrace();
                }
            }
        }
    }

    private void loadModel() {
        String classificationModelPath = getCacheDir().getAbsolutePath() + File.separator + Config.ModelName;  // 获取asset文件夹的目录
        Utils.copyFileFromAsset(MyService.this, Config.ModelName, classificationModelPath);

        // load the model
        try {
            tfLiteClassificationUtil = new TFLiteClassificationUtil(classificationModelPath);
            Toast.makeText(MyService.this, "load model succeeded", Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            Toast.makeText(MyService.this, "load model failed", Toast.LENGTH_SHORT).show();
            e.printStackTrace();
        }
    }

    private void calculate() throws Exception {                            // 模型预测和频率修改的函数
        float fps = 0F;

        long all1 = System.currentTimeMillis();   // 此处开始发送socket获取信息
        String response = ServerUtil.sendSocket("1");
        String[] values = response.split(" ");

        int bigFreq = Integer.parseInt(values[0]);
        int littleFreq = Integer.parseInt(values[1]);
        int curFPS = Integer.parseInt(values[2]);
        int mem = Integer.parseInt(values[3]);
        double littleUtil = Double.parseDouble(values[4]);
        double bigUtil = Double.parseDouble(values[5]);

        long all2 = System.currentTimeMillis();
        Log.d(TAG, "getting all information takes " + (all2 - all1) + " ms");

        // 到此处结束获取信息
        int[] big_freq_list = Config.allowedBigFrequencies;
        int[] little_freq_list = Config.allowedLittleFrequencies;

        int[] shape = {1, Config.ModelInputNum};        //  模型的输入的shape
        int[] shape2 = {1, Config.ModelActionNum};        //  模型的输出的shape

        float[] input;

        input = new float[]{(float) littleFreq / little_freq_list[little_freq_list.length - 1], (float) bigFreq / big_freq_list[big_freq_list.length - 1], (float) curFPS / Config.TargetFPS, (float) (littleUtil + bigUtil) / 8, Math.round(mem * 1.0 / 100000) / 100.0F};
        Log.d(TAG, Arrays.toString(input));

        x.loadArray(input, new int[]{Config.ModelInputNum});
        y = TensorBuffer.createFixedSize(shape2, DataType.FLOAT32);      // tensorbuffer所特有的加载方式

        long t1 = System.currentTimeMillis();
        tfLiteClassificationUtil.predict(x.getFloatArray(), y.getBuffer());    // 进行预测的代码
        long t2 = System.currentTimeMillis();
        Log.d(TAG, "prediction takes " + (t2 - t1) + " ms");

        int choice = 0;                                                 // 这部分找到结果中的最大值及其下标
        float max = Float.MIN_VALUE;
        for (int i = 0; i < y.getFloatArray().length; i++) {
            if (y.getFloatArray()[i] > max) {
                max = y.getFloatArray()[i];
                choice = i;
            }
        }

        int choice_coordinator = -1;
        t1 = System.currentTimeMillis();
        if (curFPS < Config.TargetFPS - 1)  {   // 因为帧率没有达到要求，触发了scheduler和coordinator
            response = ServerUtil.sendSocket("4");
            choice_coordinator = Integer.parseInt(response);
        } else if (choice == last_choice) {
            Log.d(TAG, "same as the last set");
            return;
        }
        t2 = System.currentTimeMillis();
        Log.d(TAG, "scheduler takes " + (t2 - t1) + "ms");

        t1 = System.currentTimeMillis();
        CPUFreqSetting.setFreq(choice, choice_coordinator);
        last_choice = choice;
        t2 = System.currentTimeMillis();

        Log.d(TAG, "setting frequency takes " + (t2 - t1) + "ms");
    }
}
