import jadx.api.*;
import jadx.api.impl.NoOpCodeCache;
import java.io.File;
import java.nio.file.*;
import java.util.*;

/** Supplemental bulk export using the exact JADX JAR selected by REA. */
class BulkExport {
  public static void main(String[] args) throws Exception {
    Path output=Path.of(args[1]);
    Files.createDirectories(output);
    JadxArgs config=new JadxArgs();
    config.setInputFile(new File(args[0]));
    config.setOutDir(output.toFile());
    config.setThreadsCount(1);
    config.setCodeCache(NoOpCodeCache.INSTANCE);
    config.setDeobfuscationOn(false);
    config.setShowInconsistentCode(true);
    config.setSkipResources(false);
    long start=System.currentTimeMillis();
    try(JadxDecompiler jadx=new JadxDecompiler(config)) {
      jadx.load();
      System.out.println("LOADED classes="+jadx.getClasses().size()+" resources="+jadx.getResources().size());
      int saved=0, existing=0, suppressed=0, failed=0, checked=0;
      List<String> failures=new ArrayList<>();
      List<JavaClass> classes=new ArrayList<>(jadx.getClasses());
      classes.sort(Comparator.comparing((JavaClass c)->!c.getRawName().startsWith("com.mgs.carparking.")).thenComparing(JavaClass::getFullName));
      for(JavaClass cls:classes) {
        checked++;
        try {
          Path destination=output.resolve("sources").resolve(cls.getFullName().replace('.', '/')+".java").normalize();
          if(!destination.startsWith(output.resolve("sources").normalize())) throw new IllegalArgumentException("Unsafe generated class path");
          if(Files.exists(destination) && Files.size(destination)>0) {existing++; continue;}
          if(cls.isNoCode()) {suppressed++; continue;}
          String code=cls.getCode();
          if(code.isBlank()) {suppressed++; continue;}
          Files.createDirectories(destination.getParent());
          Files.writeString(destination,code);
          saved++;
        } catch(Exception failure) {failed++;failures.add(cls.getRawName()+"\t"+failure);}
        finally {cls.unload();}
        if(checked%100==0) {
          System.out.println("PROGRESS checked="+checked+"/"+classes.size()+" saved="+saved+" existing="+existing+" suppressed="+suppressed+" failed="+failed);
          for(JavaClass loaded:classes) loaded.unload();
        }
      }
      Files.write(output.resolve("export-failures.txt"),failures);
      String result="{\"engine\":\"JADX "+JadxDecompiler.getVersion()+"\",\"top_level_classes\":"+jadx.getClasses().size()+",\"resources\":"+jadx.getResources().size()+",\"errors\":"+jadx.getErrorsCount()+",\"warnings\":"+jadx.getWarnsCount()+",\"elapsed_ms\":"+(System.currentTimeMillis()-start)+",\"threads\":1,\"show_inconsistent_code\":true,\"automatic_deobfuscation\":false,\"resumed_existing_files\":"+existing+",\"new_files\":"+saved+",\"suppressed_classes\":"+suppressed+",\"failed_classes\":"+failed+",\"initial_bulk_pass_interrupted_for_heap_pressure\":false}";
      Files.writeString(output.resolve("export-result.json"),result);
      jadx.printErrorsReport();
      System.out.println("EXPORT_RESULT "+result);
    }
  }
}

