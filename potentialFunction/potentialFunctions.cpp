//
// Created by polya on 7/11/24.
//
#include "potentialFunctionPrototype.hpp"

class V2 : public potentialFunction {

public:
    V2(const std::string &coefsJsonStr):potentialFunction(){
        this->coefsJson=coefsJsonStr;
    }

public:
    void json2Coefs(const std::string &coefsJsonStr)override{
        //this part is specific for potential function V2
        std::stringstream ss;
        ss<<coefsJsonStr;
        boost::property_tree::ptree pt;
        try {
            boost::property_tree::read_json(ss, pt);
            // Access data from the property tree
            this->a1=pt.get<double>("a1");
            this->a2=pt.get<double>("a2");
            this->c1=pt.get<double>("c1");
            this->c2=pt.get<double>("c2");

        }
        catch (boost::property_tree::json_parser_error &e) {
            std::cerr << "Error parsing JSON: " << e.what() << std::endl;
            std::exit(10);
        }

    }//end of json2Coefs()

    double operator()(const double &L, const double &y0, const double &z0, const double &y1) const override {
        //this part is specific for potential function V2
        double val = c1 * std::pow(y0 - a1, 2) + c2 * std::pow(z0 - a2, 2)
                     + c1 * std::pow(y1 - a1, 2) + c2 * std::pow(-y0 - z0 - y1 + L - a2, 2);
//        std::cout<<"val="<<val<<std::endl;
        return val;

    }
    void init() override{
            this->json2Coefs(coefsJson);
            std::cout << "a1=" << a1 << ", a2=" << a2 << ", c1=" << c1 << ", c2=" << c2 << std::endl;
        }
public:
    double a1;
    double a2;
    double c1;
    double c2;
    std::string coefsJson;
};

//factory function

std::shared_ptr<potentialFunction>  createPotentialFunction(const std::string& funcName, const std::string &coefsJsonStr) {
    if (funcName == "V2") {

        return std::make_shared<V2>(coefsJsonStr);
    }

    else {
        throw std::invalid_argument("Unknown potential function type");
    }
}