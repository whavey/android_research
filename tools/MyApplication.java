package com.luckystars.haircolorchanger.app;

import android.app.Application;

public class MyApplication extends Application {

    /* renamed from: c  reason: collision with root package name */
    public static int f11256c;

    /* renamed from: d  reason: collision with root package name */
    public static int f11257d;

    public void onCreate() {
        super.onCreate();
        f11256c = getResources().getDisplayMetrics().widthPixels;
        f11257d = getResources().getDisplayMetrics().heightPixels;
    }
}
