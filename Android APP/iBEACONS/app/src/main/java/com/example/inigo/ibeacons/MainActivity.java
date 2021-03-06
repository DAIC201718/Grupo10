package com.example.inigo.ibeacons;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.content.Context;
import android.content.DialogInterface;
import android.content.pm.PackageManager;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.AsyncTask;
import android.os.RemoteException;
import android.os.StrictMode;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.app.AlertDialog;
import android.webkit.WebView;

import org.altbeacon.beacon.Beacon;
import org.altbeacon.beacon.BeaconConsumer;
import org.altbeacon.beacon.BeaconManager;
import org.altbeacon.beacon.BeaconParser;
import org.altbeacon.beacon.Identifier;
import org.altbeacon.beacon.MonitorNotifier;
import org.altbeacon.beacon.RangeNotifier;
import org.altbeacon.beacon.Region;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.DataOutputStream;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.Collection;

public class MainActivity extends AppCompatActivity implements BeaconConsumer {

    protected static final String TAG = "MonitoringActivity";
    private BeaconManager beaconManager;
    public static final int MY_PERMISSIONS_REQUEST_LOCATION = 99;

    public static String urlAdress = "http://192.168.1.41:8080";
    public static final String ALTBEACON = "m:2-3=beac,i:4-19,i:20-21,i:22-23,p:24-24,d:25-25";
    public static final String ALTBEACON2 = "m:2-3=0215,i:4-19,i:20-21,i:22-23,p:24-24,d:25-25";
    public static final String EDDYSTONE_TLM =  "x,s:0-1=feaa,m:2-2=20,d:3-3,d:4-5,d:6-7,d:8-11,d:12-15";
    public static final String EDDYSTONE_UID = "s:0-1=feaa,m:2-2=00,p:3-3:-41,i:4-13,i:14-19";
    public static final String EDDYSTONE_URL = "s:0-1=feaa,m:2-2=10,p:3-3:-41,i:4-20v";
    public static final String IBEACON = "m:2-3=0215,i:4-19,i:20-21,i:22-23,p:24-24";

    private boolean isNetworkConnected() {
        ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);

        return cm.getActiveNetworkInfo() != null;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);
        BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (! mBluetoothAdapter.isEnabled()) {
            mBluetoothAdapter.enable();
        }
//        setContentView(R.layout.activity_main);
        WebView webview = new WebView(this);
        setContentView(webview);
        webview.loadUrl("https://www.eroski.es/");

        try {
            InetAddress giriAddress = InetAddress.getByName("google.com");
            String address = giriAddress.getHostAddress();
            urlAdress+=address+"/ibeacon_location";
            Log.e(address,address);

        } catch (UnknownHostException e) {
            e.printStackTrace();
        }
//        Log.i("internet",String.valueOf(isNetworkConnected()));
//        if (checkLocationPermission()) {
//            beaconManager = BeaconManager.getInstanceForApplication(this);
//            beaconManager.getBeaconParsers().add(new BeaconParser().setBeaconLayout(ALTBEACON));
//            beaconManager.getBeaconParsers().add(new BeaconParser().setBeaconLayout(ALTBEACON2));
//            beaconManager.getBeaconParsers().add(new BeaconParser().setBeaconLayout(EDDYSTONE_TLM));
//            beaconManager.getBeaconParsers().add(new BeaconParser().setBeaconLayout(EDDYSTONE_UID));
//            beaconManager.getBeaconParsers().add(new BeaconParser().setBeaconLayout(EDDYSTONE_URL));
//            beaconManager.getBeaconParsers().add(new BeaconParser().setBeaconLayout(IBEACON));
//
//            beaconManager.bind(this);
//        }else{
//            Log.i(TAG, "ERROR ON PERMISSIONS, DAMMIT");
//        }

    }

//    public static boolean isNetworkOnline(Context con) {
//        boolean status = false;
//        try {
//            ConnectivityManager cm = (ConnectivityManager) con
//                    .getSystemService(Context.CONNECTIVITY_SERVICE);
//            NetworkInfo netInfo = cm.getNetworkInfo(0);
//
//            if (netInfo != null && netInfo.getState() == NetworkInfo.State.CONNECTED) {
//                status = true;
//            } else {
//                netInfo = cm.getNetworkInfo(1);
//
//                if (netInfo != null && netInfo.getState() == NetworkInfo.State.CONNECTED) {
//                    status = true;
//                } else {
//                    status = false;
//                }
//            }
//
//        } catch (Exception e) {
//            e.printStackTrace();
//            return false;
//        }
//
//        return status;
//    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        beaconManager.unbind(this);
    }

    public void sendMessage(final JSONObject jsonParam) {

        class sendJSON implements Runnable{
            JSONObject jsonParam;
            sendJSON(JSONObject jsonParam_) {jsonParam=jsonParam_;}
            @Override
            public void run() {
                    try {
                        URL url = new URL(urlAdress);
                        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                        conn.setRequestMethod("POST");
                        conn.setRequestProperty("Content-Type", "application/json;charset=UTF-8");
                        conn.setRequestProperty("Accept", "application/json");
                        conn.setDoOutput(true);
                        conn.setDoInput(true);


                        Log.i("JSON", jsonParam.toString());
                        DataOutputStream os = new DataOutputStream(conn.getOutputStream());
                        //os.writeBytes(URLEncoder.encode(jsonParam.toString(), "UTF-8"));
                        os.writeBytes(jsonParam.toString());

                        os.flush();
                        os.close();

                        Log.i("STATUS", String.valueOf(conn.getResponseCode()));
                        Log.i("MSG", conn.getResponseMessage());

                        conn.disconnect();
                    } catch (Exception e) {
                        e.printStackTrace();
                        Log.e("STATUS", "ERRROORRR");
                    }
            }
        }
        Thread t = new Thread(new sendJSON(jsonParam));
        t.start();
//        https://stackoverflow.com/questions/32083883/android-outputstream-os-conn-getoutputstream-crashes-app 
    }

//    class NetworkAsyncTask extends AsyncTask<Void, Void, Void> {
//
//        @Override
//        protected Void doInBackground(Void... params) {
//
//                try {
//                    URL url = new URL("http://127.0.0.1:8080/ibeacon_location");
//                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
//                    conn.setRequestMethod("POST");
//                    conn.setRequestProperty("Content-Type", "application/json;charset=UTF-8");
//                    conn.setRequestProperty("Accept", "application/json");
//                    conn.setDoOutput(true);
//                    conn.setDoInput(true);
//
//                    JSONObject jsonParam = new JSONObject();
//                    jsonParam.put("timestamp", 1488873360);
//                    jsonParam.put("uname", "values_RT");
////                    jsonParam.put("message", message.getMessage());
//                    jsonParam.put("latitude", 0D);
//                    jsonParam.put("longitude", 0D);
//
//                    Log.i("JSON", jsonParam.toString());
//                    DataOutputStream os = new DataOutputStream(conn.getOutputStream());
//                    //os.writeBytes(URLEncoder.encode(jsonParam.toString(), "UTF-8"));
//                    os.writeBytes(jsonParam.toString());
//
//                    os.flush();
//                    os.close();
//
//                    Log.i("STATUS", String.valueOf(conn.getResponseCode()));
//                    Log.i("MSG", conn.getResponseMessage());
//
//                    conn.disconnect();
//                } catch (Exception e) {
//                    e.printStackTrace();
//                    Log.e("STATUS", "ERRROORRR");
//                }
//
//            return null;
//        }
//    }


//    @Override
//    public void onBeaconServiceConnect() {
//        beaconManager.addMonitorNotifier(new MonitorNotifier() {
//            @Override
//            public void didEnterRegion(Region region) {
//                Log.i(TAG, "I just saw an beacon for the first time!");
//            }
//
//            @Override
//            public void didExitRegion(Region region) {
//                Log.i(TAG, "I no longer see an beacon");
//            }
//
//            @Override
//            public void didDetermineStateForRegion(int state, Region region) {
//                Log.i(TAG, "I have just switched from seeing/not seeing beacons: "+state);
//            }
//        });
//
//        try {
//            beaconManager.startMonitoringBeaconsInRegion(new Region("myMonitoringUniqueId", null, null, null));
//        } catch (RemoteException e) {    }
//    }
    @Override
    public void onBeaconServiceConnect() {
        beaconManager.addRangeNotifier(new RangeNotifier() {
            @Override
            public void didRangeBeaconsInRegion(Collection<Beacon> beacons, Region region) {
                if (beacons.size() > 0) {
                    JSONObject jsonParam = new JSONObject();
//                    jsonParam.put("timestamp", 1488873360);
//                    jsonParam.put("uname", "values_RT");
////                    jsonParam.put("message", message.getMessage());
//                    jsonParam.put("latitude", 0D);
//                    jsonParam.put("longitude", 0D);
                    for (Beacon beacon : beacons){
                        Log.i(TAG, String.valueOf(beacon.getBluetoothAddress()));
                        try {
                            jsonParam.put(String.valueOf(beacon.getBluetoothAddress()),beacon.getDistance());
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                    sendMessage(jsonParam);
//                    Log.i(TAG, "The first beacon I see is about "+beacons.iterator().next().getDistance()+" meters away.");
//                    Log.i(TAG, Integer.toString(beacons.size()));
                }else{
                    Log.i(TAG, "No beacons FOUND");
                }
            }
        });
        try {
//            beaconManager.startRangingBeaconsInRegion(new Region("myRangingUniqueId", Identifier.parse("2F234454-CF6D-4A0F-ADF2-F4911BA9FFA6"), Identifier.parse("1"), null));
//            beaconManager.startRangingBeaconsInRegion(new Region("myRangingUniqueId", Identifier.parse("A7AE2EB7-1F00-4168-B99B-A749BAC1CA64"), null, null));
            beaconManager.startRangingBeaconsInRegion(new Region("myMonitoringUniqueId", null, null, null));
        } catch (RemoteException e) {   }
    }

    public boolean checkLocationPermission() {
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.ACCESS_COARSE_LOCATION)
                != PackageManager.PERMISSION_GRANTED) {

            // Should we show an explanation?
            if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                    Manifest.permission.ACCESS_COARSE_LOCATION)) {

                // Show an explanation to the user *asynchronously* -- don't block
                // this thread waiting for the user's response! After the user
                // sees the explanation, try again to request the permission.
                new AlertDialog.Builder(this)
                        .setTitle("IBeacon")
                        .setMessage("PERMISSIONS")
                        .setPositiveButton("OK", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialogInterface, int i) {
                                //Prompt the user once explanation has been shown
                                ActivityCompat.requestPermissions(MainActivity.this,
                                        new String[]{Manifest.permission.ACCESS_COARSE_LOCATION},
                                        MY_PERMISSIONS_REQUEST_LOCATION);
                            }
                        })
                        .create()
                        .show();


            } else {
                // No explanation needed, we can request the permission.
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.ACCESS_COARSE_LOCATION},
                        MY_PERMISSIONS_REQUEST_LOCATION);
            }
            return false;
        } else {
            return true;
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode,
                                           String permissions[], int[] grantResults) {
        switch (requestCode) {
            case MY_PERMISSIONS_REQUEST_LOCATION: {
                // If request is cancelled, the result arrays are empty.
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {

                    // permission was granted, yay! Do the
                    // location-related task you need to do.
                    if (ContextCompat.checkSelfPermission(this,
                            Manifest.permission.ACCESS_COARSE_LOCATION)
                            == PackageManager.PERMISSION_GRANTED) {

                        //Set up the BeaconManager
                        beaconManager = BeaconManager.getInstanceForApplication(this);
                        beaconManager.getBeaconParsers().add(new BeaconParser().setBeaconLayout("m:2-3=0215,i:4-19,i:20-21,i:22-23,p:24-24"));
                        beaconManager.bind(this);
                    }
                } else {
                    // permission denied, boo! Disable the
                    // functionality that depends on this permission.
                }
                return;
            }
        }
    }
}


