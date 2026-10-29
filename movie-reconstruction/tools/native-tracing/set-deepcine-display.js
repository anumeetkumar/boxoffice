import Java from 'frida-java-bridge';
rpc.exports={async setenglish(){return new Promise(resolve=>Java.perform(()=>{const U=Java.use('com.mgs.carparking.util.UserUtils');U.C0(Java.use('java.lang.String').$new('en'));resolve({display_language:String(U.n()),api_profile_to_be_supplied_by_ready_build:'hi'});}));}};
