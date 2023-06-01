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

    TensorBuffer x =  TensorBuffer.createDynamic(DataType.FLOAT32);
    TensorBuffer y =  TensorBuffer.createDynamic(DataType.FLOAT32);
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
                0, notificationIntent,  PendingIntent.FLAG_IMMUTABLE);
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
    public void onCreate(){
        super.onCreate();

        Context context = getApplicationContext();
        Intent intent = new Intent(context,MyService.class);
        context.startForegroundService(intent);

        try {                                                // 这部分载入模型
            long t1 = System.currentTimeMillis();
            loadModel();
            long t2 = System.currentTimeMillis();
            Log.d(TAG,"load model takes " + (t2 - t1) + " ms");
        } catch (Exception e) {
            e.printStackTrace();
        }

        SystemInformationUtils.setGovernorToPerformance();

        try {
            sit = new SchedulerAndGovernorThread(Config.view);    // 启动调频的线程
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        sit.start();
    }

    @Override
    public void onDestroy(){
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
        Log.d(TAG,"Service and Thread destroyed");

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

    public class SchedulerAndGovernorThread extends Thread{
        private String view;
        private  String pid ;
        private String tid_list_str;
        private boolean isStop = false;
        public SchedulerAndGovernorThread(String view) throws InterruptedException {
            this.view = view;

        }

        public void setStop(){
            isStop = true;
        }

        @Override
        public void run(){
            boolean currentViewIsOrNot = false;
            String currentActivity = null;

            while(!ServerUtil.checkServerAlive1()){
                Log.d(TAG, "Open Server Failed, Please Wait all TIME_WAIT socket terminated\n Or Server view is not right");
                try {
                    ServerUtil.startServer();
                    Thread.sleep(5000);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
            while(!isStop){
                if(!currentViewIsOrNot) {    // 如果当前的view不是想要的view
                    do {   // 开始循环获得当前的view
                        try {
                            Thread.sleep(1000);
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                        currentActivity = SystemInformationUtils.getCurrentFocusWindow();
                        Log.d(TAG, "current view is " + currentActivity);
                    } while ((currentActivity.length() <= 24) || !currentActivity.substring(0, 24).equals(view.substring(0, 24)));  // 判断当前前台是否是抖音，如果不是，则继续循环
                    // 能出循环说明当前已经是抖音里面了
                    try {
                        Thread.sleep(4000);
//                        SystemInformationUtils.init(view);  // init 如果失败，说明当前不在抖音中，或者此时很卡
                        String currentPid = SystemInformationUtils.getCurrentForegroundAppPid();
                        if(!Objects.equals(this.pid, currentPid)){
                            pid = currentPid;
                            String renderThreadTid = SystemInformationUtils.getRenderThreadTid(pid);
                            String surfaceflingerTid = SystemInformationUtils.getSurfaceFlinger();
                            this.tid_list_str = pid+','+renderThreadTid+','+surfaceflingerTid;
                        }
                        currentViewIsOrNot = true;
                    } catch (Exception e) {
                        e.printStackTrace();
                        continue;                           // 从头开始
                    }
                }

                try {                                       // 能走到这里，说明已经init成功了
                    Thread.sleep(1000);
                    // get pid list
                    long t1 = System.currentTimeMillis();
                    Log.d(TAG,"===========begin==============");
                    calculate(tid_list_str);                            // 使用模型计算下一次的频率以及设置频率
                    Log.d(TAG,"===========over==============");
                    long t2 = System.currentTimeMillis();
                    Log.d(TAG,"total time takes " + (t2 - t1) + " ms");

                } catch (Exception e) {
                    currentViewIsOrNot = false;
                    Log.d(TAG,"Unkown Error");
                    e.printStackTrace();
                }
            }
        }
    }

    private void loadModel() {
        //String classificationModelPath = getCacheDir().getAbsolutePath() + File.separator + "model.tflite";  // 获取asset文件夹的目录
        //Utils.copyFileFromAsset(MyService.this, "model.tflite", classificationModelPath);
        String classificationModelPath = getCacheDir().getAbsolutePath() + File.separator + "model_oneplus9pro.tflite";  // 获取asset文件夹的目录
        Utils.copyFileFromAsset(MyService.this, "model_oneplus9pro.tflite", classificationModelPath);
        // load the model
        try {
            tfLiteClassificationUtil = new TFLiteClassificationUtil(classificationModelPath);
            Toast.makeText(MyService.this, "load model succeeded", Toast.LENGTH_SHORT).show();
        } catch (Exception e) {
            Toast.makeText(MyService.this, "load model failed", Toast.LENGTH_SHORT).show();
            e.printStackTrace();
        }
    }

    private void calculate(String tid_list_str) throws Exception {                            // 模型预测和频率修改的函数
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
        Log.d(TAG,"getting all information takes " + (all2- all1) + " ms");
        // 到此处结束获取信息


        if (curFPS< 50) {   // 若帧率过低，则本轮进行调度
            int [] big_freq_list = Config.allowedBigFrequencies;
            int [] little_freq_list = Config.allowedLittleFrequencies;
            Scheduler scheduler = new Scheduler(tid_list_str, big_freq_list,little_freq_list);
            ArrayList<Double> commu_info = scheduler.schedule(bigFreq, littleFreq);
            Coordinator coordinator = new Coordinator(big_freq_list, little_freq_list);
            double[] temp1 = coordinator.coordinate(commu_info, bigUtil, littleUtil, bigFreq, littleFreq);
            CPUFreqSetting.setFreq((int) (temp1[1] * 3 + temp1[3]));
        } else {   // 若帧率正常，则本轮进行调频
            int[] shape = {1, 5};        //  模型的输入的shape
            int[] shape2 = {1, 16};        //  模型的输出的shape

            float[] input = {(float)littleFreq / 1766400,(float)bigFreq/ 2649600,(float) curFPS/ 60, (float) (littleUtil + bigUtil) / 8, Math.round(mem * 1.0 / 400000) / 10.0F}; // 构建inpt
//
            Log.d(TAG, Arrays.toString(input));

            x.loadArray(input, new int[]{5});
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

            t1 = System.currentTimeMillis();

            Log.d(TAG, "current choice is " + choice);
            if (choice == last_choice) {
                Log.d(TAG, "same as the last set");
                return;
            }

            CPUFreqSetting.setFreq(choice);
            last_choice = choice;
            t2 = System.currentTimeMillis();

            Log.d(TAG, "setting frequency takes " + (t2 - t1) + "ms");
        }
    }
}
