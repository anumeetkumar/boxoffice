import com.android.tools.smali.dexlib2.*;import com.android.tools.smali.dexlib2.dexbacked.*;import com.android.tools.smali.dexlib2.iface.*;import com.android.tools.smali.dexlib2.writer.builder.*;import com.android.tools.smali.dexlib2.writer.io.*;import com.android.tools.smali.baksmali.*;import com.android.tools.smali.baksmali.Adaptors.*;import com.android.tools.smali.baksmali.formatter.*;import com.android.tools.smali.smali.*;import org.antlr.runtime.*;import org.antlr.runtime.tree.*;import java.nio.file.*;import java.nio.charset.*;import java.util.*;import java.util.zip.*;import java.util.regex.*;import java.io.*;
class BoxOfficeEndpointVariant {
 static final Set<String> targets=Set.of("Ln9/b;","Lsa/b0$a;","Lsa/o0;");
 static String text(ClassDef d)throws Exception{StringWriter s=new StringWriter();BaksmaliWriter w=new BaksmaliWriter(s);new ClassDefinition(new BaksmaliOptions(),d).writeTo(w);w.flush();return s.toString();}
 static String modify(String cls,String s){
  if(cls.equals("Ln9/b;")){String from="\"https://moviein.ajfysu.com/\"";if(s.indexOf(from)<0||s.indexOf(from)!=s.lastIndexOf(from))throw new IllegalStateException("Default endpoint anchor");return s.replace(from,"\"https://deepcineph.7nkznc.com/\"");}
  if(cls.equals("Lsa/o0;")){String from="\"KEY_PREF_USER_TOKEN\"";if((s.length()-s.replace(from,"").length())/from.length()!=2)throw new IllegalStateException("Token isolation anchors");return s.replace(from,"\"KEY_PREF_USER_TOKEN_DEEPCINE_V1\"");}
  Pattern p=Pattern.compile("invoke-static \\{\\}, Lsa/o0;->m\\(\\)Ljava/lang/String;\\s*(?:\\.line \\d+\\s*)*move-result-object ([vp]\\d+)");Matcher m=p.matcher(s);if(!m.find())throw new IllegalStateException("Language header anchor");String reg=m.group(1);s=m.replaceFirst(Matcher.quoteReplacement("const-string "+reg+", \"hi\""));
  String anchor="    invoke-virtual {v2}, Lokhttp3/Request$Builder;->build()Lokhttp3/Request;";if(s.indexOf(anchor)<0||s.indexOf(anchor)!=s.lastIndexOf(anchor))throw new IllegalStateException("Request builder anchor");
  String route="""
    # Enforce the selected endpoint after the cached/global domain interceptor.
    invoke-interface {p1}, Lokhttp3/Interceptor$Chain;->request()Lokhttp3/Request;
    move-result-object v0
    invoke-virtual {v0}, Lokhttp3/Request;->url()Lokhttp3/HttpUrl;
    move-result-object v0
    invoke-virtual {v0}, Lokhttp3/HttpUrl;->newBuilder()Lokhttp3/HttpUrl$Builder;
    move-result-object v0
    const-string v1, "https"
    invoke-virtual {v0, v1}, Lokhttp3/HttpUrl$Builder;->scheme(Ljava/lang/String;)Lokhttp3/HttpUrl$Builder;
    const-string v1, "deepcineph.7nkznc.com"
    invoke-virtual {v0, v1}, Lokhttp3/HttpUrl$Builder;->host(Ljava/lang/String;)Lokhttp3/HttpUrl$Builder;
    const/16 v1, 0x1bb
    invoke-virtual {v0, v1}, Lokhttp3/HttpUrl$Builder;->port(I)Lokhttp3/HttpUrl$Builder;
    invoke-virtual {v0}, Lokhttp3/HttpUrl$Builder;->build()Lokhttp3/HttpUrl;
    move-result-object v0
    invoke-virtual {v2, v0}, Lokhttp3/Request$Builder;->url(Lokhttp3/HttpUrl;)Lokhttp3/Request$Builder;
""";
  s=s.replace(anchor,route+anchor);
  if(Boolean.getBoolean("endpoint.diagnostic")){
   String log="""
    :endpoint_diag_start
    const-wide/16 v0, 0x2000
    invoke-virtual {p1, v0, v1}, Lokhttp3/Response;->peekBody(J)Lokhttp3/ResponseBody;
    move-result-object v0
    invoke-virtual {v0}, Lokhttp3/ResponseBody;->string()Ljava/lang/String;
    move-result-object v0
    new-instance v1, Lorg/json/JSONObject;
    invoke-direct {v1, v0}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V
    const-string v0, "msg"
    invoke-virtual {v1, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    const-string v2, "BoxEndpointMsg"
    invoke-static {v2, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    const-string v0, "message"
    invoke-virtual {v1, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    invoke-static {v2, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :endpoint_diag_end
    goto :endpoint_diag_done
    .catch Ljava/lang/Exception; {:endpoint_diag_start .. :endpoint_diag_end} :endpoint_diag_catch
    :endpoint_diag_catch
    move-exception v0
    :endpoint_diag_done
""";
   s=s.replace("    invoke-virtual {p1}, Lokhttp3/Response;->code()I",log+"    invoke-virtual {p1}, Lokhttp3/Response;->code()I");
  }
  return s;
 }
 static void assemble(String s,DexBuilder builder,int api)throws Exception{try(InputStreamReader reader=new InputStreamReader(new ByteArrayInputStream(s.getBytes(StandardCharsets.UTF_8)),StandardCharsets.UTF_8)){smaliFlexLexer l=new smaliFlexLexer(reader,api);l.sourceFile=new File("endpoint-variant.smali");CommonTokenStream t=new CommonTokenStream(l);smaliParser p=new smaliParser(t);var r=p.smali_file();if(p.state.syntaxErrors>0||l.lexerErrors>0)throw new IllegalStateException("Smali parse");CommonTreeNodeStream n=new CommonTreeNodeStream(r.tree);n.tokens=t;smaliTreeWalker w=new smaliTreeWalker(n);w.opcodes=new Opcodes(api);w.dexBuilder=builder;w.smali_file();if(w.state.syntaxErrors>0)throw new IllegalStateException("Smali assemble");}}
 public static void main(String[]args)throws Exception{Path out=Path.of(args[1]);Files.createDirectories(out);List<String> changes=new ArrayList<>();
  try(ZipFile z=new ZipFile(args[0])){for(var es=z.entries();es.hasMoreElements();){var e=es.nextElement();if(!e.getName().matches("classes[0-9]*\\.dex"))continue;byte[] bytes=z.getInputStream(e).readAllBytes();DexBackedDexFile dex=new DexBackedDexFile(bytes,0);boolean selected=false;for(int i=0;i<dex.classCount;i++)if(targets.contains(((ClassDef)dex.classSection.get(i)).getType()))selected=true;if(!selected)continue;
   int version=Integer.parseInt(new String(bytes,4,3,StandardCharsets.US_ASCII)),api=switch(version){case 35->23;case 37->24;case 38->26;case 39->28;default->throw new IllegalStateException("DEX format");};DexBuilder builder=new DexBuilder(new Opcodes(api));
   for(int i=0;i<dex.classCount;i++){ClassDef d=(ClassDef)dex.classSection.get(i);String before=text(d),after=targets.contains(d.getType())?modify(d.getType(),before):before;assemble(after,builder,api);if(!before.equals(after)){String name=d.getType().substring(1,d.getType().length()-1).replace('/','_');Files.writeString(out.resolve(name+".before.smali"),before);Files.writeString(out.resolve(name+".after.smali"),after);changes.add(e.getName()+"\t"+d.getType());}if(i%1500==0)System.out.println(e.getName()+" "+i+"/"+dex.classCount);}
   FileDataStore store=new FileDataStore(out.resolve(e.getName()).toFile());try{builder.writeTo(store);}finally{store.raf.close();}System.out.println("Reassembled "+e.getName());
  }}if(changes.size()!=3)throw new IllegalStateException("Expected three narrowly scoped classes, got "+changes.size());Files.write(out.resolve("changes.tsv"),changes);
 }
}
