### frida 설치
pip install frida-tools (에뮬레이터는 arm translation tool 설치 된 상태로 동적 분석할 apk가 설치되어 있는 상태여야 한다.)

###  anti-vm 우회 스크립트 작성
(https://note-ing.tistory.com/m/62)해당 사이트를 참고하여 분석 후 gpt를 이용하여 작성
``` // anti-vm-bypass.js

Java.perform(function () {
  // Build 클래스 가져오기
  var Build = Java.use("android.os.Build");

  // Build.TAGS 값을 후킹하여 "release-keys" 반환
  Object.defineProperty(Build, "TAGS", {
    get: function () {
      return "release-keys";
    },
  });
  console.log("Build.TAGS hooked successfully.");

  // File 클래스 가져오기
  var File = Java.use("java.io.File");

  // File.exists() 메서드 후킹
  File.exists.implementation = function () {
    var path = this.getPath();
    if (path === "/system/app/Superuser.apk") {
      console.log(
        "File.exists() called for /system/app/Superuser.apk - returning false"
      );
      return false;
    }
    return this.exists();
  };
  console.log("File.exists hooked successfully.");

  // /proc/tty/drivers 파일 내용 우회
  var FileInputStream = Java.use("java.io.FileInputStream");
  FileInputStream.read.overload("[B").implementation = function (buffer) {
    var path = this.getFD().sync();
    if (path === "/proc/tty/drivers") {
      var fakeData = "dummy".getBytes();
      fakeData.copy(buffer, 0, 0, fakeData.length);
      console.log(
        "FileInputStream.read() called for /proc/tty/drivers - returning fake data"
      );
      return fakeData.length;
    }
    return this.read(buffer);
  };
  console.log("/proc/tty/drivers file content hooked successfully.");

  // 특정 클래스와 메서드 후킹
  var b = Java.use("com.ldjSxw.heBbQd.a.b");

  // k(Context) 메서드를 후킹하여 항상 false 반환
  b.k.implementation = function (context) {
    console.log(
      "com.ldjSxw.heBbQd.a.b.k() called - returning false to bypass root detection"
    );
    return false;
  };
  console.log("com.ldjSxw.heBbQd.a.b.k() hooked successfully.");
});
```
### frida 서버 준비
- 이후에 알아본 바로 arm 형식의 파일은 translation tool을 설치해도 안되서 frida-server-16.2.5-x86.xz파일을 사용
- (https://github.com/frida/frida/releases/tag/16.2.5) 해당 링크에서 에뮬레이터 아키텍쳐에 맞는 frida-server.xz다운로드 하여 에뮬레이터에 업로드 하고 실행

- frida 서버 에뮬레이터에 업로드
  - adb push frida-server-<version>-android-x86 /data/local/tmp/
- frida 서버 권한 부여
  - adb shell "chmod 755 /data/local/tmp/frida-server-<version>-android-x86"
- Frida 서버 실행
  - adb shell "/data/local/tmp/frida-server-<version>-android-x86 &"
### frida 스크립트 실행
- 다른 파워쉘을 킨 후 frida 스크립트 실행. 
`com.example.myapp` 부분에는 복호화 후 리패키징한 apk 파일을 jadx로 여셔서 `AndoriodManifest.xml` 파일의 패키지 이름 확인하신 후 해당 이름을 넣기.
- frida -U -f com.ldjSxw.heBbQd -l anti-vm-byapss.js
![initial](https://github.com/user-attachments/assets/81828099-6ab2-4ee1-a18a-b69ed2cc866d)
### 결론
- 에뮬레이터에서 앱이 실행되는 것을 확인할 수 있음
- vm에서 실행되지 않고 분석을 할 수 없었던 것을 위의 과정을 거쳐 해결할 수 있었음
![initial)](https://github.com/user-attachments/assets/3f6d318b-98c8-4f88-8343-be0a1e79bbfe)
