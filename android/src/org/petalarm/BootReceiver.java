package org.petalarm;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

/**
 * Android 开机广播接收器
 * 当设备重启后自动启动应用，使闹钟功能在重启后仍能正常工作
 * 用户需要先手动打开一次应用，之后每次重启都会自动启动
 */
public class BootReceiver extends BroadcastReceiver {
    private static final String TAG = "PetAlarm BootReceiver";
    
    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null || intent.getAction() == null) {
            return;
        }
        
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            Log.i(TAG, "Boot completed received, starting Pet Alarm app");
            
            try {
                Intent launchIntent = context.getPackageManager()
                    .getLaunchIntentForPackage(context.getPackageName());
                
                if (launchIntent != null) {
                    launchIntent.addFlags(
                        Intent.FLAG_ACTIVITY_NEW_TASK
                        | Intent.FLAG_ACTIVITY_CLEAR_TOP
                    );
                    context.startActivity(launchIntent);
                    Log.i(TAG, "Pet Alarm app started successfully");
                } else {
                    Log.w(TAG, "No launch intent found for package");
                }
            } catch (Exception e) {
                Log.e(TAG, "Failed to start app: " + e.getMessage());
            }
        }
    }
}
