

import android.content.Context
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.FileChannel

class StrokeDetector(context: Context) : AutoCloseable {

    private val interpreter: Interpreter

    init {
        val modelBuffer = loadModelFile(context, "model.tflite")
        interpreter = Interpreter(modelBuffer)
    }

    private fun loadModelFile(context: Context, modelName: String): ByteBuffer {
        val assetFileDescriptor = context.assets.openFd(modelName)
        val inputStream = FileInputStream(assetFileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = assetFileDescriptor.startOffset
        val declaredLength = assetFileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }

    fun predict(input: FloatArray): Float {
        val inputBuffer = ByteBuffer.allocateDirect(4 * input.size).apply {
            order(ByteOrder.nativeOrder())
            input.forEach { putFloat(it) }
            rewind()
        }

        val output = Array(1) { FloatArray(1) }
        interpreter.run(inputBuffer, output)
        return output[0][0]
    }

    override fun close() {
        interpreter.close()
    }
}
