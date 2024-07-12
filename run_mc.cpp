#include "./mc_subroutine/mc_read_load_compute.hpp"
#include "./potentialFunction/potentialFunctionPrototype.hpp"
int main(int argc, char *argv[]) {
    if (argc != 2) {
        std::cout << "wrong arguments" << std::endl;
        std::exit(2);
    }
    auto mcObj=mc_computation(std::string(argv[1]));
    mcObj.init_and_run();

//    int paramIndStart=1;


//    std::string TStr=std::string(argv[paramIndStart]);
//    std::cout<<"TStr="<<TStr<<std::endl;
//
//    std::string coefsJsonStr=std::string(argv[paramIndStart+1]);
//    std::cout<<"coefsJsonStr="<<coefsJsonStr<<std::endl;
//
//    std::string funcNameStr=std::string(argv[paramIndStart+2]);
//    std::cout<<"funcNameStr="<<funcNameStr<<std::endl;
//
//    std::string jsonToCppInitValsStr=std::string(argv[paramIndStart+3]);
//    std::cout<<"jsonToCppInitValsStr="<<jsonToCppInitValsStr<<std::endl;
//
//    std::string loopToWriteStr=std::string(argv[paramIndStart+4]);
//    std::cout<<"loopToWriteStr="<<loopToWriteStr<<std::endl;
//
//    std::string newFlushNumStr=std::string(argv[paramIndStart+5]);
//    std::cout<<"newFlushNumStr="<<newFlushNumStr<<std::endl;
//
//    std::string loopLastFileStr=std::string(argv[paramIndStart+6]);
//    std::cout<<"loopLastFileStr="<<loopLastFileStr<<std::endl;
//
//    std::string TDirRootStr=std::string(argv[paramIndStart+7]);
//    std::cout<<"TDirRootStr="<<TDirRootStr<<std::endl;
//
//    std::string U_dist_dataDirStr=std::string(argv[paramIndStart+8]);
//    std::cout<<"U_dist_dataDirStr="<<U_dist_dataDirStr<<std::endl;
//
//
//    auto mcObj=mc_computation(TStr,coefsJsonStr,funcNameStr,
//                              jsonToCppInitValsStr,loopToWriteStr,newFlushNumStr,
//                              loopLastFileStr,TDirRootStr,U_dist_dataDirStr);



}