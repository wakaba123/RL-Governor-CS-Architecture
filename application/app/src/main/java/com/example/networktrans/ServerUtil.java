package com.example.networktrans;

import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class ServerUtil {
    public static String BinaryServerPosition = Config.BinaryServerPosition;
    public static String TAG = "ServerUtil";

    public static String sendSocket(String message) {
        String response = null;
        try {
            // 创建Socket连接
            Socket socket = new Socket(Config.SERVER_IP, Config.SERVER_PORT);

            // 发送请求消息给服务器
            BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            OutputStream output = socket.getOutputStream();

            // 发送消息到服务器
            output.write(message.getBytes());
            output.flush();
            System.out.println("Sent message: " + message);

            // 接收服务器响应
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            response = in.readLine();
            String TAG = "ServerUtil";
            Log.d(TAG, "收到服务器消息: " + response);

            // 关闭连接
            socket.close();
        } catch (IOException e) {
            e.printStackTrace();
            Log.d(TAG, "发送socket请求失败");
            return "failed";
        }
        return response;
    }

    public static int startServer() throws InterruptedException {
        Path path = Paths.get(BinaryServerPosition);

        if (!Files.exists(path)) {
            Log.d(TAG,"Server file not exist!");
            return -1;
        }

        Log.d(TAG,"Server file found");
        // nohup /data/local/tmp/server > /data/local/tmp/server.log 2>&1 &
        CommandExecution.easyExec("nohup" +" " +  BinaryServerPosition + " " + Config.view +  " > /data/local/tmp/server.log 2>&1 &", true);

        return 0;
    }

    public static boolean checkServerAlive1() {
        String res = sendSocket("2");
        if (res == null){
            return false;
        }
        Log.d(TAG, "Server view is " + res);
        return res.equals(Config.view);
    }

    public static void stopServer() {
       sendSocket("3");
    }

}
