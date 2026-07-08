package com.clock2reactnative;

import android.app.Application;
import android.content.Context;
import android.content.res.Resources;

import com.facebook.react.ReactPackage;
import com.facebook.react.shell.MainPackageConfig;
import com.facebook.react.shell.MainReactPackage;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;

public class PackageList {
  private Application application;
  private MainPackageConfig mConfig;

  public PackageList(Application application) {
    this(application, null);
  }

  public PackageList(Application application, MainPackageConfig config) {
    this.application = application;
    mConfig = config;
  }

  public List<ReactPackage> getPackages() {
    return new ArrayList<>(Arrays.<ReactPackage>asList(
      new MainReactPackage(mConfig)
    ));
  }
}
