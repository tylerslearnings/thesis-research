import QuantitativeAnalyzer
import QualitativeAnalyzer
from sklearn.neural_network.multilayer_perceptron import MLPClassifier

def main():
    name = "apple inc"
    associatedDates, revenueList, profitList, stockGrowth, dividenGrowth, marketGrowth, yearGrowth = QuantitativeAnalyzer.PerformAnalysis(name)

    companyScores, productScores, ceoScores = QualitativeAnalyzer.PerformAnalysis(name, associatedDates)

    TrainingValues = []
    TestValues = []
    trainingAnswers = yearGrowth[0:len(yearGrowth) / 2]
    testAnswers = yearGrowth[len(yearGrowth) / 2:]

    print len(trainingAnswers)
    print len(testAnswers)

    for i in range(0, len(associatedDates) / 2):
        list = []
        list.append(revenueList[i])
        list.append(profitList[i])
        list.append(stockGrowth[i])
        list.append(dividenGrowth[i])
        list.append(marketGrowth[i])
        list.append(companyScores[i])
        list.append(productScores[i])
        list.append(ceoScores[i])
        TrainingValues.append(list)

    for i in range(len(associatedDates) / 2, len(associatedDates)):
        list = []
        list.append(revenueList[i])
        list.append(profitList[i])
        list.append(stockGrowth[i])
        list.append(dividenGrowth[i])
        list.append(marketGrowth[i])
        list.append(companyScores[i])
        list.append(productScores[i])
        list.append(ceoScores[i])
        TestValues.append(list)
    perceptron = MLPClassifier(algorithm='l-bfgs', alpha=1e-5, hidden_layer_sizes=(5, 2),random_state=1)

    #perceptron.fit(TrainingValues, )

   # for testData in


#TODO: Obtain Qualitative Scores

if __name__ == '__main__':
    main()

