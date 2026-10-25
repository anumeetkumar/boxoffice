import java.net.*;
import java.nio.channels.*;
class LoopbackProbe {
  public static void main(String[] args) throws Exception {
    try (ServerSocket server=new ServerSocket(0,1,InetAddress.getLoopbackAddress());
         Socket client=new Socket(InetAddress.getLoopbackAddress(),server.getLocalPort());
         Socket accepted=server.accept()) {
      System.out.println("TCP loopback OK: "+server.getInetAddress());
    }
    System.out.println("Socket temp: "+System.getProperty("jdk.net.unixdomain.tmpdir"));
    Pipe pipe=Pipe.open();pipe.source().close();pipe.sink().close();
    System.out.println("NIO pipe OK");
    try(Selector selector=Selector.open()) {System.out.println("NIO selector OK");}
  }
}
